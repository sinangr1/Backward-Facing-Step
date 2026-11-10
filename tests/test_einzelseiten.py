"""Tests für sechs getrennte deutsche Live-Präsentationsseiten."""
import json
import sys
from pathlib import Path
from threading import Thread
from urllib.request import Request, build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s01_parameter import Parameter
from s06_simulation import Simulation
from s08_einzelseite import SEITEN, InteraktiveEinzelseite, bild_als_png
from s09_webseiten import server_erzeugen


def test_jede_einzelseite_zeichnet_genau_ein_diagramm():
    for nummer in SEITEN:
        sim = Simulation(Parameter().with_h(1.0))
        sim.step(4)
        png = bild_als_png(sim, nummer)
        assert png[:8] == b'\x89PNG\r\n\x1a\n', nummer
        assert len(png) > 10000, nummer


def test_animation_und_stufenhoehe_auf_einzelseite():
    simulation = Simulation(Parameter().with_h(1.0))
    fenster = InteraktiveEinzelseite(simulation, seitennummer=3, schritte_pro_bild=3)
    assert len(fenster.abbildung.axes) == 4  # Diagramm + Regler + zwei Schaltflächen
    fenster.naechstes_bild()
    assert simulation.t > 0
    fenster.regler.set_val(1.4)
    assert simulation.par.h == 1.4 and simulation.t == 0
    fenster.naechstes_bild()
    assert simulation.t > 0
    fenster.pause_umschalten()
    zeit = simulation.t
    fenster.naechstes_bild()
    assert simulation.t == zeit
    fenster.neu_starten()
    assert simulation.t == 0
    plt.close(fenster.abbildung)


def test_getrennte_browserseiten_und_unabhaengiger_zustand():
    server = server_erzeugen(port=0, schritte_pro_bild=3)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    client = build_opener(HTTPCookieProcessor(CookieJar()))
    try:
        for nummer in range(1, 7):
            with client.open(f'{base}/seite/{nummer}') as antwort:
                html = antwort.read().decode('utf-8')
                assert f'Präsentationsseite {nummer} von 6' in html
                assert html.count('id="livebild"') == 1
                assert 'Stufenhöhe' in html

        with client.open(f'{base}/api/bild/1?h=1.0&schritte=4') as antwort:
            assert antwort.read(8) == b'\x89PNG\r\n\x1a\n'
            erste = json.loads(antwort.headers['X-CFD-Status'])
        assert erste['zeit'] > 0
        with client.open(f'{base}/api/bild/2?h=1.0&schritte=4') as antwort:
            antwort.read()
            zweite = json.loads(antwort.headers['X-CFD-Status'])
        assert zweite['zeit'] > 0
        with client.open(f'{base}/api/bild/1?h=1.4&schritte=0') as antwort:
            antwort.read()
            neu = json.loads(antwort.headers['X-CFD-Status'])
        assert neu['hoehe'] == pytest.approx(1.4)
        assert neu['zeit'] == pytest.approx(0)
        with client.open(f'{base}/api/bild/2?h=1.0&schritte=0') as antwort:
            antwort.read()
            zweite_nachher = json.loads(antwort.headers['X-CFD-Status'])
        assert zweite_nachher['zeit'] == pytest.approx(zweite['zeit'])

        payload = json.dumps({'h': 0.7}).encode('utf-8')
        anfrage = Request(f'{base}/api/neustart/3', data=payload,
                          headers={'Content-Type': 'application/json'}, method='POST')
        with client.open(anfrage) as antwort:
            assert json.load(antwort)['hoehe'] == pytest.approx(.7)
        with client.open(f'{base}/api/bild/3?h=0.7&schritte=0') as antwort:
            antwort.read()
            neu3 = json.loads(antwort.headers['X-CFD-Status'])
        assert neu3['hoehe'] == pytest.approx(.7)
        assert neu3['zeit'] == pytest.approx(0)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
