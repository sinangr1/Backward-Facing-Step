"""Hauptprogramm für sechs voneinander unabhängige CFD-Präsentationsseiten.

python 00_pipeline.py                                  # Startseite im Browser
python 00_pipeline.py --seite 3                       # Nur Stromlinien als Fenster
python 00_pipeline.py --seite 5 --gif wirbel.gif      # Einzelanimation als GIF
python 00_pipeline.py --druckloeser sor               # SOR aus der Vorlesung
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Sechs getrennte, zeitabhängige CFD-Präsentationsseiten zur rückwärtsgerichteten Stufe')
    parser.add_argument('--seite', type=int, choices=range(1, 7), metavar='1..6',
                        help='Ein einzelnes Diagramm als Matplotlib-Fenster starten')
    parser.add_argument('--h', type=float, default=1.0, help='Anfangsstufenhöhe')
    parser.add_argument('--druckloeser', choices=['lu', 'sor'], default='lu',
                        help='Drucklöser: LU oder SOR aus der Vorlesung')
    parser.add_argument('--schritte-pro-bild', type=int, default=8,
                        help='Berechnete Zeitschritte je Animationsbild')
    parser.add_argument('--intervall', type=int, default=170,
                        help='Zeitraum zwischen Bildern im Einzelfenster (ms)')
    parser.add_argument('--anschluss', type=int, default=8765,
                        help='Lokaler Anschluss des Präsentationsservers')
    parser.add_argument('--kein-browser', action='store_true',
                        help='Startseite nicht automatisch öffnen')
    parser.add_argument('--gif', type=str, default=None,
                        help='Eine einzelne animierte Auswertung als GIF speichern (nur mit --seite)')
    parser.add_argument('--bilder', type=int, default=24,
                        help='Anzahl der GIF-Bilder')
    parser.add_argument('--bilder-pro-sekunde', type=int, default=5,
                        help='Bildfrequenz des GIF')
    parser.add_argument('--hoehenvariation', action='store_true',
                        help='Stufenhöhe im GIF von 0,5 bis 1,5 variieren')
    argumente = parser.parse_args()
    if argumente.gif and not argumente.seite:
        parser.error('Für eine einzelne GIF-Animation ist --seite 1..6 erforderlich.')
    if argumente.schritte_pro_bild < 0 or argumente.bilder < 1 or argumente.bilder_pro_sekunde < 1:
        parser.error('Die Schritt- und Bildzahlen müssen gültige positive Zahlen sein.')

    # Ohne Auswahl öffnet die Hauptpipeline die Startseite mit sechs Links.
    # Auf jeder Unterseite wird genau ein einziges Diagramm animiert.
    if argumente.seite is None:
        from s09_webseiten import starten
        starten(port=argumente.anschluss, druckloeser=argumente.druckloeser,
                schritte_pro_bild=argumente.schritte_pro_bild,
                browser_oeffnen=not argumente.kein_browser)
        return

    if argumente.gif:
        import matplotlib
        matplotlib.use('Agg')
    from dataclasses import replace
    from s01_parameter import Parameter
    from s06_simulation import Simulation
    from s08_einzelseite import InteraktiveEinzelseite, SEITEN

    parameter = replace(Parameter(), pressure_method=argumente.druckloeser).with_h(argumente.h)
    simulation = Simulation(parameter)
    anzeige = InteraktiveEinzelseite(simulation, seitennummer=argumente.seite,
                                   schritte_pro_bild=argumente.schritte_pro_bild,
                                   intervall=argumente.intervall)
    print(f'Präsentationsseite {argumente.seite}: {SEITEN[argumente.seite][0]}')
    print(f'Stufenhöhe = {parameter.h:.2f} · Reynolds-Zahl = {parameter.Re:g} · '
          f'Drucklöser = {parameter.pressure_method.upper()}')
    if argumente.gif:
        pfad = anzeige.gif_speichern(argumente.gif,
                                      anzahl_bilder=argumente.bilder,
                                      bilder_pro_sekunde=argumente.bilder_pro_sekunde,
                                      hoehenvariation=argumente.hoehenvariation)
        print(f'Einzelanimation gespeichert: {pfad}')
        import matplotlib.pyplot as plt
        plt.close(anzeige.abbildung)
    else:
        print('Der Regler ändert die Stufenhöhe; das Strömungsfeld wird neu berechnet.')
        anzeige.anzeigen()


if __name__ == '__main__':
    main()
