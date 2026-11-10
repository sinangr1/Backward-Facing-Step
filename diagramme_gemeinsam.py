"""Gemeinsame Koordinaten und Farbbereiche für alle sechs Diagramme."""
import numpy as np
from matplotlib.colors import Normalize

SPEED_LIMIT=(0,2)
PRESSURE_LIMIT=(-1.25,1.25)
OMEGA_LIMIT=(-8,8)
TAU_LIMIT=(-.08,.08)


def channel(ax, sim, title):
    p = sim.par
    ax.set_facecolor('#dfe3e8')
    ax.plot([0,p.x_step,p.x_step,p.xlength],[p.h,p.h,0,0],color='#1f2937',lw=1.2,zorder=8)
    ax.plot([0,p.xlength],[p.ylength,p.ylength],color='#1f2937',lw=1.2,zorder=8)
    ax.set(xlim=(0,p.xlength),ylim=(0,p.ylength),title=title)
    ax.set_xlabel('x / L_ref',fontsize=8)
    ax.set_ylabel('y / L_ref',fontsize=8)
    ax.tick_params(labelsize=8)
    ax.set_aspect('equal',adjustable='box')


def meshplot(ax,sim,data,*,cmap,vmin,vmax,title):
    g = sim.g
    m=ax.pcolormesh(g.xe,g.ye,np.ma.masked_invalid(data),shading='flat',
                    cmap=cmap,vmin=vmin,vmax=vmax,rasterized=True)
    channel(ax,sim,title)
    return m
