"""05 – Druck-Poisson-Gleichung und MAC-Projektion.

Laplace(p) = rho/dt · div(F, G).
Feste Wände und Einlass: dp/dn = 0; offener Auslass: p = 0.
LU faktorisiert die Matrix einmalig; SOR verwendet omg, eps und itermax.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from s03_randbedingungen import apply_bc


def divergence(u, v, g):
    return (u[:, 1:]-u[:, :-1])/g.dx+(v[1:, :]-v[:-1, :])/g.dy


class PressureSolver:
    def __init__(self, g, par):
        self.g, self.par = g, par
        index = np.full(g.fluid.shape, -1, dtype=int)
        index[g.fluid] = np.arange(g.fluid.sum())
        rows, cols, vals = [], [], []
        diagonal = np.zeros_like(g.fluid, float)
        for j, i in zip(*np.where(g.fluid)):
            k, d = index[j, i], 0.0
            for dj, di, c in ((0, -1, 1/g.dx**2), (0, 1, 1/g.dx**2),
                              (-1, 0, 1/g.dy**2), (1, 0, 1/g.dy**2)):
                jj, ii = j+dj, i+di
                if 0 <= jj < g.ny and 0 <= ii < g.nx and g.fluid[jj, ii]:
                    rows.append(k); cols.append(index[jj,ii]); vals.append(-c)
                    d += c
            if i == g.nx-1:   # Am Auslass p = 0: Abstand Zellmitte–Rand gleich dx/2.
                d += 2/g.dx**2
            diagonal[j, i] = d
            rows.append(k); cols.append(k); vals.append(d)
        self.A = coo_matrix((vals,(rows,cols)),shape=(g.fluid.sum(),)*2).tocsc()
        self.diagonal = diagonal
        self.lu = splu(self.A) if par.pressure_method == 'lu' else None
        jj, ii = np.indices(g.fluid.shape)
        self.red = g.fluid & ((jj+ii)%2 == 0)
        self.black = g.fluid & ~self.red
        self.p_previous = np.zeros_like(g.fluid, float)
        self.iterations = 0
        self.converged = True

    def _solve_sor(self, rhs):
        g, par = self.g, self.par
        p = self.p_previous.copy()
        b = np.zeros_like(p)
        b[g.fluid] = rhs
        mask = g.fluid
        # Rot-Schwarz-SOR: pro Iteration werden beide Schachbrettmuster aktualisiert.
        for it in range(1, par.itermax+1):
            old_p = p.copy()
            for select in (self.red, self.black):
                west = np.zeros_like(p); east = np.zeros_like(p)
                south = np.zeros_like(p); north = np.zeros_like(p)
                west[:,1:] = p[:,:-1] * (mask[:,1:] & mask[:,:-1])
                east[:,:-1] = p[:,1:] * (mask[:,:-1] & mask[:,1:])
                south[1:,:] = p[:-1,:] * (mask[1:,:] & mask[:-1,:])
                north[:-1,:] = p[1:,:] * (mask[:-1,:] & mask[1:,:])
                update = (b+(west+east)/g.dx**2+(south+north)/g.dy**2) / np.where(mask, self.diagonal, 1)
                p[select] = (1-par.omg)*p[select] + par.omg*update[select]
            if it % 10 == 0 or it == par.itermax:
                residual = np.max(np.abs(self.A@p[mask]-rhs))
                # Absolute Toleranz eps aus der Vorlesungsfolie für das Druckresiduum.
                if residual <= par.eps:
                    break
        self.iterations = it
        self.p_previous = p
        return p

    def project(self, F, G, dt):
        g, par = self.g, self.par
        rhs = -(par.rho/dt)*divergence(F, G, g)[g.fluid]
        p = np.zeros(g.fluid.shape)
        if self.lu is not None:
            p[g.fluid] = self.lu.solve(rhs)
            self.iterations = 1
        else:
            p = self._solve_sor(rhs)
        u, v = F.copy(), G.copy()
        u[:,1:-1] -= dt/par.rho * np.diff(p, axis=1)/g.dx*g.u_open[:,1:-1]
        v[1:-1,:] -= dt/par.rho * np.diff(p, axis=0)/g.dy*g.v_open[1:-1,:]
        u[:,-1] += dt/par.rho * 2*p[:,-1]/g.dx*g.u_open[:,-1]
        apply_bc(u, v, g, par)
        error = float(np.max(np.abs(self.A@p[g.fluid]-rhs)))
        self.converged = error <= (par.eps if par.pressure_method == 'sor' else 1e-8)
        return u,v,p,error
