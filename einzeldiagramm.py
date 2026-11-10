"""Alle sechs Diagramm-Skripte als eigenständige lebendige Präsentationsseiten."""
import argparse
from s01_parameter import Parameter
from s06_simulation import Simulation


def run(draw):
    """Passende Seitennummer aus der Zeichenfunktion bestimmen und einzeln anzeigen."""
    from s08_einzelseite import SEITEN, InteraktiveEinzelseite
    nummer = next((n for n, (_, _, funktion) in SEITEN.items()
                   if funktion.__code__.co_filename == draw.__code__.co_filename), None)
    if nummer is None:
        raise ValueError('Diese Diagrammfunktion ist nicht registriert.')
    parser = argparse.ArgumentParser(description='Ein animiertes CFD-Diagramm anzeigen')
    parser.add_argument('--h', type=float, default=1.0, help='Stufenhöhe')
    parser.add_argument('--schritte-pro-bild', type=int, default=8,
                        help='Berechnete Zeitschritte je Animationsbild')
    parser.add_argument('--intervall', type=int, default=170,
                        help='Zeitabstand zwischen Bildern in Millisekunden')
    argumente = parser.parse_args()
    simulation = Simulation(Parameter().with_h(argumente.h))
    InteraktiveEinzelseite(simulation, nummer, argumente.schritte_pro_bild,
                          argumente.intervall).anzeigen()
