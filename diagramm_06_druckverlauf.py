"""Diagramm 6 – Druckverlauf entlang einer Linie auf Höhe der Einlassmitte."""
import numpy as np


def draw(ax,sim,f):
    p,g=sim.par,sim.g
    ax.plot(g.x, f['pressure_line'],color='#13669c',lw=1.8)
    ax.axvline(p.x_step,color='#666',ls='--',lw=1,label='Stufe')
    ax.axhline(0,color='#aaa',lw=.7)
    ax.set(xlim=(0,p.xlength),xlabel='x / L_ref',ylabel='p / (ρ U_ref²)',
           title=f'6 · Druckverlauf (y={f["yline"]:.2f})')
    ax.grid(alpha=.22)
    ax.set_box_aspect(.25)
    ax.tick_params(labelsize=8)
    if np.any(np.isfinite(f['pressure_line'])):
        lo,hi=np.nanmin(f['pressure_line']),np.nanmax(f['pressure_line'])
        pad=max(.2,.12*(hi-lo))
        ax.set_ylim(max(-10,lo-pad),min(10,hi+pad))
    return None

if __name__ == '__main__':
    from einzeldiagramm import run
    run(draw)
