"""Diagramm 3 – Stromlinien des in jedem Zeitschritt berechneten Geschwindigkeitsfeldes."""
import numpy as np
from matplotlib.colors import ListedColormap
from diagramme_gemeinsam import channel


def draw(ax,sim,f):
    g=sim.g
    ax.pcolormesh(g.xe,g.ye,np.ma.masked_where(~g.fluid,np.ones(g.fluid.shape)),
                  cmap=ListedColormap(['#ecf7ff']),vmin=0,vmax=2,shading='flat')
    # Im Festkörper ist die Geschwindigkeit null; dort verlaufen keine Stromlinien.
    uc=np.where(g.fluid,f['uc'],0.)
    vc=np.where(g.fluid,f['vc'],0.)
    # Startpunkte nur im Strömungsgebiet platzieren.
    inlet_y=np.linspace(sim.par.h+0.5*g.dy,sim.par.ylength-0.5*g.dy,17)
    inlet_seed=np.column_stack([np.full(inlet_y.size,g.x[1]),inlet_y])
    downstream_seed=np.column_stack([np.full(7,sim.par.x_step+1.5),
                                     np.linspace(.25,1.45,7)])
    seeds=np.vstack([inlet_seed,downstream_seed])
    ax.streamplot(g.x,g.y,uc,vc,color='#135e9a',density=1.6,
                  start_points=seeds,linewidth=.8,arrowsize=.8,
                  minlength=.06,maxlength=8)
    channel(ax,sim,'3 · Stromlinien')
    return None

if __name__ == '__main__':
    from einzeldiagramm import run
    run(draw)
