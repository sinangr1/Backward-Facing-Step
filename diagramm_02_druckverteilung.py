"""Diagramm 2 – Statischer Druck, normiert mit rho · U_ref²."""
from diagramme_gemeinsam import meshplot, PRESSURE_LIMIT


def draw(ax,sim,f):
    return meshplot(ax,sim,f['pressure'],cmap='coolwarm',vmin=PRESSURE_LIMIT[0],
                    vmax=PRESSURE_LIMIT[1],title='2 · Druckverteilung p / (ρ U_ref²)')

if __name__ == '__main__':
    from einzeldiagramm import run
    run(draw)
