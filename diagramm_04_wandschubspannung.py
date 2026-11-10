"""Diagramm 4 – Wandschubspannung ausschließlich entlang der Festkörperwände."""
from matplotlib.collections import LineCollection
from diagramme_gemeinsam import meshplot, TAU_LIMIT
from s07_auswertung import wall_shear_segments


def draw(ax,sim,f):
    # Die graue Geschwindigkeitsdarstellung dient nur als Hintergrundinformation.
    meshplot(ax,sim,f['speed'],cmap='Greys',vmin=0,vmax=4,
             title='4 · Wandschubspannung τ_w')
    segments,values=wall_shear_segments(sim,f)
    lc=LineCollection(segments,cmap='coolwarm',linewidths=3.8,zorder=10)
    lc.set_clim(*TAU_LIMIT)
    lc.set_array(values)
    ax.add_collection(lc)
    ax.text(.99,.91,'Farbige Linien: Wandwerte',transform=ax.transAxes,
            ha='right',va='top',fontsize=7,color='#192c40',
            bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
    return lc

if __name__ == '__main__':
    from einzeldiagramm import run
    run(draw)
