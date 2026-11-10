"""06 – Zeitintegration, CFL-Bedingung, Druckprojektion und Erhaltungsprüfung."""
from dataclasses import dataclass, field
import numpy as np
from s02_geometrie import make_grid
from s03_randbedingungen import initial_fields, apply_bc
from s04_impuls import choose_dt, intermediate
from s05_druck import PressureSolver, divergence


@dataclass
class Simulation:
    par: object
    g: object = field(init=False)
    solver: object = field(init=False)
    u: np.ndarray = field(init=False)
    v: np.ndarray = field(init=False)
    p: np.ndarray = field(init=False)
    t: float = 0
    n: int = 0
    last_residual: float = 0
    history: list = field(default_factory=list)

    def __post_init__(self):
        self.g = make_grid(self.par)
        self.solver = PressureSolver(self.g,self.par)
        self.u,self.v,self.p = initial_fields(self.g,self.par)

    def step(self, count=1):
        for _ in range(count):
            if self.t >= self.par.t_end:
                break
            apply_bc(self.u,self.v,self.g,self.par)
            dt = min(choose_dt(self.u,self.v,self.g,self.par), self.par.t_end-self.t)
            F,G = intermediate(self.u,self.v,dt,self.g,self.par)
            self.u,self.v,self.p,self.last_residual = self.solver.project(F,G,dt)
            if not (np.isfinite(self.u).all() and np.isfinite(self.v).all() and np.isfinite(self.p).all()):
                raise FloatingPointError('Numerische Instabilität: NaN oder unendlicher Wert.')
            self.t += dt; self.n += 1
            if self.n % 10 == 0 or self.n == 1:
                self.history.append(self.diagnostics())
        return self

    def diagnostics(self):
        g = self.g
        q_in = float(self.u[:,0].sum()*g.dy)
        q_out = float(self.u[:,-1].sum()*g.dy)
        div = float(np.max(np.abs(divergence(self.u,self.v,g)[g.fluid])))
        return dict(t=self.t, step=self.n, q_in=q_in, q_out=q_out,
                    mass_error=abs(q_out-q_in)/max(abs(q_in),1e-12),
                    div_max=div, pressure_residual=self.last_residual,
                    iterations=self.solver.iterations,
                    pressure_converged=self.solver.converged)

    def change_h(self,h):
        # Neue Geometrie → neue Poisson-Matrix → Anfangszustand und Zeit zurücksetzen.
        self.par = self.par.with_h(h)
        self.t,self.n,self.history = 0.0,0,[]
        self.__post_init__()
        return self
