"""08 – Eine unabhängige, zeitabhängige Darstellung pro Diagramm.

Jede Seite erhält eine eigene Simulation. Eine Stufenhöhenänderung setzt das
Strömungsfeld und die Poisson-Matrix neu auf; es werden keine Bilder ausgetauscht.
"""
from io import BytesIO
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.widgets import Button, Slider

from s07_auswertung import fields
from diagramme_gemeinsam import SPEED_LIMIT, PRESSURE_LIMIT, TAU_LIMIT, OMEGA_LIMIT
from diagramm_01_geschwindigkeitsbetrag import draw as zeichne_geschwindigkeit
from diagramm_02_druckverteilung import draw as zeichne_druck
from diagramm_03_stromlinien import draw as zeichne_stromlinien
from diagramm_04_wandschubspannung import draw as zeichne_wandschubspannung
from diagramm_05_wirbelstaerke import draw as zeichne_wirbelstaerke
from diagramm_06_druckverlauf import draw as zeichne_druckverlauf


SEITEN = {
    1: ('Geschwindigkeitsbetrag', 'Betrag des Geschwindigkeitsvektors |u|', zeichne_geschwindigkeit),
    2: ('Druckverteilung', 'Räumliche Druckverteilung p', zeichne_druck),
    3: ('Stromlinien', 'Stromlinien im Geschwindigkeitsfeld', zeichne_stromlinien),
    4: ('Wandschubspannung', 'Schubspannung an den festen Wänden', zeichne_wandschubspannung),
    5: ('Wirbelstärke', 'Wirbelstärke ω_z = ∂v/∂x − ∂u/∂y', zeichne_wirbelstaerke),
    6: ('Druckverlauf', 'Druck entlang der Kanallängsachse', zeichne_druckverlauf),
}

FARBSKALEN = {
    1: ('turbo', SPEED_LIMIT, '|u| / U_ref'),
    2: ('coolwarm', PRESSURE_LIMIT, 'p / (ρ U_ref²)'),
    4: ('coolwarm', TAU_LIMIT, 'τ_w'),
    5: ('RdBu_r', OMEGA_LIMIT, 'ω_z · L_ref / U_ref'),
}


def diagramm_zeichnen(achse, simulation, seitennummer):
    """Genau ein Diagramm mit dem aktuellen Lösungszustand zeichnen."""
    if seitennummer not in SEITEN:
        raise ValueError('Die Seitennummer muss zwischen 1 und 6 liegen.')
    funktion = SEITEN[seitennummer][2]
    achse.clear()
    return funktion(achse, simulation, fields(simulation))


def farbskala_anlegen(abbildung, achse, seitennummer):
    """Eine unveränderliche Farbskala erlaubt Vergleiche zwischen verschiedenen h."""
    if seitennummer not in FARBSKALEN:
        return None
    farbkarte, grenzen, beschriftung = FARBSKALEN[seitennummer]
    scalar = ScalarMappable(norm=Normalize(*grenzen), cmap=farbkarte)
    farbleiste = abbildung.colorbar(scalar, ax=achse, shrink=.66, pad=.02, aspect=22)
    farbleiste.set_label(beschriftung, fontsize=10)
    return farbleiste


def status_text(simulation):
    diagnose = simulation.diagnostics()
    return (f'Stufenhöhe h = {simulation.par.h:.2f}  ·  '
            f'Re = {simulation.par.Re:g}  ·  '
            f'Zeit t = {simulation.t:.3f}  ·  '
            f'Zeitschritte = {simulation.n}\n'
            f'Drucklöser: {simulation.par.pressure_method.upper()}  ·  '
            f'Massenbilanzfehler: {diagnose["mass_error"]:.2e}  ·  '
            f'Poisson-Residuum: {diagnose["pressure_residual"]:.2e}')


def bild_als_png(simulation, seitennummer):
    """Eine einzelne Seite für die lokalen Web-Präsentationsseiten rendern."""
    figur = Figure(figsize=(12.2, 4.65), dpi=110, facecolor='white')
    FigureCanvasAgg(figur)
    achse = figur.add_subplot(111)
    figur.subplots_adjust(left=.065, right=.91, bottom=.21, top=.75)
    diagramm_zeichnen(achse, simulation, seitennummer)
    farbskala_anlegen(figur, achse, seitennummer)
    figur.suptitle(f'{seitennummer}. {SEITEN[seitennummer][0]} · Rückwärtsgerichtete Stufe',
                   fontsize=14, fontweight='bold', x=.50, y=.975)
    figur.text(.065, .075, status_text(simulation), ha='left', va='center', fontsize=9,
               color='#334155', linespacing=1.55)
    speicher = BytesIO()
    figur.savefig(speicher, format='png', dpi=110, facecolor='white')
    return speicher.getvalue()


class InteraktiveEinzelseite:
    """Eigenständiges Matplotlib-Fenster mit h-Regler und Zeitanimation."""

    def __init__(self, simulation, seitennummer=1, schritte_pro_bild=8, intervall=170):
        if seitennummer not in SEITEN:
            raise ValueError('Die Seitennummer muss zwischen 1 und 6 liegen.')
        self.simulation = simulation
        self.seitennummer = seitennummer
        self.schritte_pro_bild = schritte_pro_bild
        self.intervall = intervall
        self.laeuft = True
        self.abbildung, self.achse = plt.subplots(figsize=(12.2, 5.4))
        self.abbildung.subplots_adjust(left=.065, right=.90, bottom=.34, top=.80)
        self.farbleiste = farbskala_anlegen(self.abbildung, self.achse, seitennummer)
        self.achse_regler = self.abbildung.add_axes([.17, .19, .50, .04])
        self.regler = Slider(self.achse_regler, 'Stufenhöhe h', .3, 1.5,
                             valinit=simulation.par.h, valstep=simulation.par.dy)
        self.achse_pause = self.abbildung.add_axes([.73, .185, .10, .06])
        self.knopf_pause = Button(self.achse_pause, 'Pause')
        self.achse_reset = self.abbildung.add_axes([.84, .185, .12, .06])
        self.knopf_reset = Button(self.achse_reset, 'Neu starten')
        self.regler.on_changed(self.h_aendern)
        self.knopf_pause.on_clicked(self.pause_umschalten)
        self.knopf_reset.on_clicked(self.neu_starten)
        self.statustext = self.abbildung.text(.08, .08, '', fontsize=9, color='#334155')
        self.animation = None
        self.zeichnen()

    def zeichnen(self):
        diagramm_zeichnen(self.achse, self.simulation, self.seitennummer)
        self.abbildung.suptitle(f'{self.seitennummer}. {SEITEN[self.seitennummer][0]}',
                                fontsize=15, fontweight='bold')
        self.statustext.set_text(status_text(self.simulation))
        self.abbildung.canvas.draw_idle()

    def h_aendern(self, wert):
        hoehe = self.simulation.par.with_h(wert).h
        if abs(self.simulation.par.h - hoehe) > 1e-9:
            self.simulation.change_h(hoehe)
            self.zeichnen()

    def pause_umschalten(self, ereignis=None):
        self.laeuft = not self.laeuft
        self.knopf_pause.label.set_text('Pause' if self.laeuft else 'Fortsetzen')

    def neu_starten(self, ereignis=None):
        self.simulation.change_h(self.regler.val)
        self.zeichnen()

    def naechstes_bild(self, bildnummer=None):
        if self.laeuft and self.simulation.t < self.simulation.par.t_end:
            self.simulation.step(self.schritte_pro_bild)
            self.zeichnen()
        return []

    def anzeigen(self):
        self.animation = FuncAnimation(self.abbildung, self.naechstes_bild,
                                       interval=self.intervall, blit=False,
                                       cache_frame_data=False)
        plt.show()

    def gif_speichern(self, ziel, anzahl_bilder=24, bilder_pro_sekunde=5,
                      hoehenvariation=False):
        ziel = Path(ziel)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        def render(bildnummer):
            if hoehenvariation:
                hoehe = self.simulation.par.with_h(np.linspace(.5, 1.5, anzahl_bilder)[bildnummer]).h
                if abs(self.simulation.par.h - hoehe) > 1e-9:
                    self.regler.set_val(hoehe)
            return self.naechstes_bild(bildnummer)
        animation = FuncAnimation(self.abbildung, render, frames=range(anzahl_bilder),
                                  interval=1000/bilder_pro_sekunde,
                                  cache_frame_data=False, repeat=False)
        animation.save(str(ziel), writer=PillowWriter(fps=bilder_pro_sekunde), dpi=90)
        return ziel
