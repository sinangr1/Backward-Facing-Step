"""04 – Expliziter Impulsschritt mit Donor-Cell-Diskretisierung.

Du/Dt = -grad(p)/rho + nu · Laplace(u).
Die Zwischengeschwindigkeiten F und G werden vor der Druckprojektion berechnet.
alpha = 0: zentrale Differenzen; alpha = 1: Aufwindverfahren.
"""
import numpy as np
from s03_randbedingungen import apply_bc


def choose_dt(u, v, g, par):
    transport = np.max(np.abs(u))/g.dx + np.max(np.abs(v))/g.dy
    diffusion = 2*par.nu*(1/g.dx**2 + 1/g.dy**2)
    return min(par.dt, par.tau/(transport+diffusion+1e-14))


def donor_flux(k, left, right, alpha):
    return k*(0.5*(left+right)+0.5*alpha*np.sign(k)*(left-right))


def intermediate(u, v, dt, g, par):
    F, G = u.copy(), v.copy()
    uc, uw, ue = u[:, 1:-1], u[:, :-2], u[:, 2:]
    un, us = np.empty_like(uc), np.empty_like(uc)
    un[:-1] = np.where(g.u_open[1:, 1:-1], u[1:, 1:-1], -uc[:-1])
    un[-1] = -uc[-1]
    us[1:] = np.where(g.u_open[:-1, 1:-1], u[:-1, 1:-1], -uc[1:])
    us[0] = -uc[0]
    ke, kw = (uc+ue)/2, (uw+uc)/2
    kn = (v[1:, :-1]+v[1:, 1:])/2
    ks = (v[:-1, :-1]+v[:-1, 1:])/2
    adv_u = (donor_flux(ke, uc, ue, par.alpha)-donor_flux(kw, uw, uc, par.alpha))/g.dx
    adv_u += (donor_flux(kn, uc, un, par.alpha)-donor_flux(ks, us, uc, par.alpha))/g.dy
    lap_u = (ue-2*uc+uw)/g.dx**2+(un-2*uc+us)/g.dy**2
    F[:, 1:-1] = np.where(g.u_open[:, 1:-1], uc+dt*(-adv_u+par.nu*lap_u), 0)

    vc, vs, vn = v[1:-1, :], v[:-2, :], v[2:, :]
    ve, vw = np.empty_like(vc), np.empty_like(vc)
    ve[:, :-1] = np.where(g.v_open[1:-1, 1:], v[1:-1, 1:], -vc[:, :-1])
    ve[:, -1] = vc[:, -1]   # Am Auslass verschwindet der Geschwindigkeitsgradient.
    vw[:, 1:] = np.where(g.v_open[1:-1, :-1], v[1:-1, :-1], -vc[:, 1:])
    vw[:, 0] = -vc[:, 0]
    ke = (u[:-1, 1:]+u[1:, 1:])/2
    kw = (u[:-1, :-1]+u[1:, :-1])/2
    kn, ks = (vc+vn)/2, (vs+vc)/2
    adv_v = (donor_flux(ke, vc, ve, par.alpha)-donor_flux(kw, vw, vc, par.alpha))/g.dx
    adv_v += (donor_flux(kn, vc, vn, par.alpha)-donor_flux(ks, vs, vc, par.alpha))/g.dy
    lap_v = (ve-2*vc+vw)/g.dx**2+(vn-2*vc+vs)/g.dy**2
    G[1:-1, :] = np.where(g.v_open[1:-1, :], vc+dt*(-adv_v+par.nu*lap_v), 0)
    F[:, -1] = F[:, -2]  # Für die Zwischengeschwindigkeit gilt du/dx = 0.
    return apply_bc(F, G, g, par)
