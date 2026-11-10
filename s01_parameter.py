"""01 – Dimensionslose Modellparameter gemäß den Vorlesungsfolien.

Re = U_ref · L_ref / nu; damit nu = U_ref · L_ref / Re.
Der angegebene Wert dt = 0,05 ist die obere Schranke des adaptiven Zeitschritts.
"""
from dataclasses import dataclass, replace, asdict


@dataclass(frozen=True)
class Parameter:
    imax: int = 100
    jmax: int = 20
    xlength: float = 10.0
    ylength: float = 2.0
    x_step: float = 2.0
    h: float = 1.0                 # Stufenhöhe; über die Bedienoberfläche veränderbar
    U_ref: float = 1.0
    L_ref: float = 1.0            # Feste Bezugslänge; NICHT die Einlasshöhe
    rho: float = 1.0
    Re: float = 100.0
    dt: float = 0.05              # Obergrenze aus der Vorlesung; wird aus Stabilitätsgründen nicht überschritten
    t_end: float = 500.0
    tau: float = 0.5              # Sicherheitsfaktor für CFL-Bedingung und Diffusion
    alpha: float = 0.9            # Gewichtung zwischen Zentraldifferenzen und Aufwindverfahren
    eps: float = 1e-3            # Abbruchschwelle für SOR-Iterationen
    omg: float = 1.7             # Successive Over-Relaxation
    itermax: int = 500
    pressure_method: str = 'lu'  # 'lu' (schnell) / 'sor' (aus der Vorlesung)

    @property
    def nu(self):
        return self.U_ref * self.L_ref / self.Re

    @property
    def dx(self):
        return self.xlength / self.imax

    @property
    def dy(self):
        return self.ylength / self.jmax

    def with_h(self, h):
        # Stufenhöhe auf Zellgrenzen des Gitters runden.
        snapped = round(float(h) / self.dy) * self.dy
        return replace(self, h=round(snapped, 8))

    def validate(self):
        if self.imax < 8 or self.jmax < 6:
            raise ValueError('Es muss imax >= 8 und jmax >= 6 gelten.')
        if not (0 < self.h < self.ylength - 2*self.dy):
            raise ValueError('Es muss 0 < h < ylength - 2*dy gelten.')
        if abs(self.h/self.dy - round(self.h/self.dy)) > 1e-8:
            raise ValueError('h muss ein Vielfaches von dy sein (with_h verwenden).')
        if abs(self.x_step/self.dx - round(self.x_step/self.dx)) > 1e-8:
            raise ValueError('x_step muss ein Vielfaches von dx sein.')
        if self.Re <= 0 or self.rho <= 0 or self.U_ref <= 0:
            raise ValueError('Re, rho und U_ref müssen positiv sein.')
        if not 0 <= self.alpha <= 1:
            raise ValueError('alpha muss im Intervall [0, 1] liegen.')
        if self.pressure_method not in ('lu', 'sor'):
            raise ValueError('Als Drucklöser ist nur lu oder sor zulässig.')
        return self

    def to_dict(self):
        return dict(asdict(self), nu=self.nu, model='Zweidimensionale inkompressible Navier-Stokes-Gleichungen; dimensionslos')
