"""Diagramm 1 – Betrag der Geschwindigkeit, normiert mit U_ref."""
from diagramme_gemeinsam import meshplot, SPEED_LIMIT


def draw(ax,sim,f):
    return meshplot(ax,sim,f['speed'],cmap='turbo',vmin=SPEED_LIMIT[0],
                    vmax=SPEED_LIMIT[1],title='1 · Geschwindigkeitsbetrag |u| / U_ref')

if __name__ == '__main__':
    from einzeldiagramm import run
    run(draw)
