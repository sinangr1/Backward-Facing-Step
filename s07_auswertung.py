"""07 – Auswertung von Geschwindigkeit, Wirbelstärke, Wandschubspannung und Druck."""
import numpy as np


def cell_velocity(sim):
    u,v = sim.u,sim.v
    return (u[:,:-1]+u[:,1:])/2, (v[:-1,:]+v[1:,:])/2


def fields(sim):
    """Alle Diagramme verwenden die berechneten Felder zum selben physikalischen Zeitpunkt."""
    g, par = sim.g,sim.par
    uc,vc = cell_velocity(sim)
    speed = np.hypot(uc,vc)/par.U_ref
    # Wirbelstärke: omega_z = dv/dx - du/dy an den Zellmittelpunkten.
    dud_y = np.gradient(uc,g.dy,axis=0)
    dvd_x = np.gradient(vc,g.dx,axis=1)
    omega = (dvd_x-dud_y)*par.L_ref/par.U_ref
    # Druckprofil auf einer konstanten Höhe in der Mitte des Einlasses.
    yline = (par.h+par.ylength)/2
    jline = int(np.argmin(np.abs(g.y-yline)))
    pressure_line = np.where(g.fluid[jline,:],sim.p[jline,:],np.nan)/(par.rho*par.U_ref**2)
    bottom_tau = np.full(g.nx,np.nan)
    active = (g.x>par.x_step) & g.fluid[0,:]
    bottom_tau[active] = 2*par.rho*par.nu*uc[0,active]/g.dy
    xr = None
    neg = np.flatnonzero(active & (bottom_tau<0))
    if neg.size:
        for i in range(neg[0],g.nx-1):
            if bottom_tau[i] < 0 <= bottom_tau[i+1]:
                xr = float(g.x[i]-bottom_tau[i]*g.dx/(bottom_tau[i+1]-bottom_tau[i]))
                break
    return dict(uc=uc,vc=vc,
                speed=np.where(g.fluid,speed,np.nan),
                pressure=np.where(g.fluid,sim.p/(par.rho*par.U_ref**2),np.nan),
                omega=np.where(g.fluid,omega,np.nan),
                pressure_line=pressure_line, yline=yline,
                bottom_tau=bottom_tau, reattachment_x=xr)


def wall_shear_segments(sim, f):
    """Die Wandschubspannung ist ausschließlich an der Wand definiert."""
    g,p = sim.g,sim.par
    uc,vc = f['uc'],f['vc']
    segments, values = [], []
    mu = p.rho*p.nu
    for j,i in zip(*np.where(g.fluid)):
        xl,xr = g.xe[i],g.xe[i+1]
        yb,yt = g.ye[j],g.ye[j+1]
        if j == 0 or not g.fluid[j-1,i]:
            segments.append([(xl,yb),(xr,yb)])
            values.append(2*mu*uc[j,i]/g.dy)
        if j == g.ny-1 or not g.fluid[j+1,i]:
            segments.append([(xl,yt),(xr,yt)])
            values.append(2*mu*uc[j,i]/g.dy)
        if i>0 and not g.fluid[j,i-1]:
            segments.append([(xl,yb),(xl,yt)])
            values.append(2*mu*vc[j,i]/g.dx)
        if i<g.nx-1 and not g.fluid[j,i+1]:
            segments.append([(xr,yb),(xr,yt)])
            values.append(2*mu*vc[j,i]/g.dx)
    return segments,np.array(values)
