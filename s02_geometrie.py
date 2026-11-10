"""02 – Rechteckiger Kanal mit rückwärtsgerichteter Stufe und versetztem MAC-Gitter.

Druck p: Zellmittelpunkte (jmax, imax).
Horizontale Geschwindigkeit u: vertikale Zellflächen (jmax, imax + 1).
Vertikale Geschwindigkeit v: horizontale Zellflächen (jmax + 1, imax).
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class Grid:
    nx: int
    ny: int
    dx: float
    dy: float
    x: np.ndarray
    y: np.ndarray
    xe: np.ndarray
    ye: np.ndarray
    fluid: np.ndarray
    u_open: np.ndarray
    v_open: np.ndarray


def make_grid(par):
    par.validate()
    nx, ny = par.imax, par.jmax
    xe = np.linspace(0, par.xlength, nx+1)
    ye = np.linspace(0, par.ylength, ny+1)
    x, y = (xe[1:]+xe[:-1])/2, (ye[1:]+ye[:-1])/2
    X, Y = np.meshgrid(x, y)
    # Vor der Stufe erhöhte Kanalsohle, dahinter Kanalboden bei y = 0.
    fluid = (X >= par.x_step) | (Y >= par.h)
    u_open = np.zeros((ny, nx+1), bool)
    v_open = np.zeros((ny+1, nx), bool)
    u_open[:, 1:-1] = fluid[:, :-1] & fluid[:, 1:]
    u_open[:, 0], u_open[:, -1] = fluid[:, 0], fluid[:, -1]
    v_open[1:-1, :] = fluid[:-1, :] & fluid[1:, :]
    return Grid(nx, ny, par.dx, par.dy, x, y, xe, ye, fluid, u_open, v_open)
