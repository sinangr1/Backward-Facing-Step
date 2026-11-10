"""03 – Anfangs- und Randbedingungen.

Links: u = 1 nur am offenen Einlass, v = 0. Rechts: freier Auslass.
Oben, unten und an der Stufe: Haftbedingung (kein Gleiten).
Anfang: in der oberen Kanalhälfte u = 1, in der unteren u = 0; überall v = 0.
"""
import numpy as np


def inlet_profile(g, par):
    return par.U_ref * g.u_open[:, 0].astype(float)


def apply_bc(u, v, g, par):
    u[~g.u_open] = 0.0
    v[~g.v_open] = 0.0
    u[:, 0] = inlet_profile(g, par)
    return u, v


def initial_fields(g, par):
    u = np.zeros((g.ny, g.nx+1))
    v = np.zeros((g.ny+1, g.nx))
    p = np.zeros((g.ny, g.nx))
    # Anfangswerte aus der Folie: obere Hälfte u = 1, untere Hälfte u = 0.
    u[:, 1:-1] = ((g.y[:, None] >= par.ylength/2) & g.u_open[:, 1:-1]) * par.U_ref
    u[:, -1] = ((g.y >= par.ylength/2) & g.u_open[:, -1]) * par.U_ref
    return (*apply_bc(u, v, g, par), p)
