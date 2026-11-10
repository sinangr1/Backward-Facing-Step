"""Diagramm 5 – Wirbelstärke omega_z = dv/dx - du/dy."""
from diagramme_gemeinsam import meshplot,OMEGA_LIMIT


def draw(ax,sim,f):
    return meshplot(ax,sim,f['omega'],cmap='RdBu_r',vmin=OMEGA_LIMIT[0],
                    vmax=OMEGA_LIMIT[1],title='5 · Wirbelstärke ω_z · L_ref/U_ref')

if __name__ == '__main__':
    from einzeldiagramm import run
    run(draw)
