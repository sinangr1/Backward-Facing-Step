"""09 – Sechs eigenständige, live berechnete Präsentationsseiten im Browser.

Für die Webserver-Grundfunktionen wird ausschließlich die Python-Standardbibliothek
verwendet. Berechnet werden dieselben Navier–Stokes-Felder wie in den Notebooks.
Die Seiten werden auf 127.0.0.1 angeboten und sind nicht öffentlich erreichbar.
"""
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit, parse_qs
import json
import re
import secrets
import webbrowser

from s01_parameter import Parameter
from s06_simulation import Simulation

VERZEICHNIS = Path(__file__).resolve().parent / 'webseite'


def server_erzeugen(host='127.0.0.1', port=8765, druckloeser='lu',
                     schritte_pro_bild=8):
    """Lokalen Server erzeugen; jede Diagrammseite hat ihren eigenen Zustand."""
    class PraesentationsServer(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    class Anfrage(BaseHTTPRequestHandler):
        server_version = 'CFD-Einzelseiten/1.0'

        def log_message(self, format, *args):
            # Keine automatischen englischen HTTP-Protokollmeldungen anzeigen.
            pass

        def antwort(self, inhalt, typ, code=200, sitzung=None, zusaetzlich=None):
            self.send_response(code)
            self.send_header('Content-Type', typ)
            self.send_header('Content-Length', str(len(inhalt)))
            self.send_header('Cache-Control', 'no-store')
            if sitzung:
                self.send_header('Set-Cookie', f'cfd_sitzung={sitzung}; Path=/; SameSite=Lax; HttpOnly')
            for schluessel, wert in (zusaetzlich or {}).items():
                self.send_header(schluessel, str(wert))
            self.end_headers()
            self.wfile.write(inhalt)

        def session_id(self):
            cookies = SimpleCookie()
            try:
                cookies.load(self.headers.get('Cookie', ''))
                sitzung = cookies.get('cfd_sitzung')
                if sitzung and re.fullmatch(r'[0-9a-f]{32}', sitzung.value):
                    return sitzung.value, None
            except Exception:
                pass
            neu = secrets.token_hex(16)
            return neu, neu

        def zustand(self, sitzung, seite):
            schluessel = (sitzung, seite)
            with self.server.zustandssperre:
                if schluessel not in self.server.zustaende:
                    parameter = Parameter(pressure_method=self.server.druckloeser).with_h(1.0)
                    self.server.zustaende[schluessel] = {
                        'simulation': Simulation(parameter), 'sperre': Lock()
                    }
                return self.server.zustaende[schluessel]

        def do_GET(self):
            url = urlsplit(self.path)
            pfad = url.path
            if pfad == '/' or pfad == '/startseite':
                self.antwort((VERZEICHNIS / 'startseite.html').read_bytes(),
                             'text/html; charset=utf-8')
                return
            if pfad == '/assets/stil.css':
                self.antwort((VERZEICHNIS / 'stil.css').read_bytes(), 'text/css; charset=utf-8')
                return
            if pfad == '/assets/steuerung.js':
                self.antwort((VERZEICHNIS / 'steuerung.js').read_bytes(),
                             'application/javascript; charset=utf-8')
                return
            einzel = re.fullmatch(r'/seite/([1-6])', pfad)
            if einzel:
                nummer = int(einzel.group(1))
                from s08_einzelseite import SEITEN
                inhalt = (VERZEICHNIS / 'einzelseite.html').read_text(encoding='utf-8')
                inhalt = inhalt.replace('%%NUMMER%%', str(nummer))
                inhalt = inhalt.replace('%%TITEL%%', SEITEN[nummer][0])
                inhalt = inhalt.replace('%%ERKLAERUNG%%', SEITEN[nummer][1])
                inhalt = inhalt.replace('%%VORHERIGE%%', str(6 if nummer == 1 else nummer-1))
                inhalt = inhalt.replace('%%NAECHSTE%%', str(1 if nummer == 6 else nummer+1))
                self.antwort(inhalt.encode('utf-8'), 'text/html; charset=utf-8')
                return
            bild = re.fullmatch(r'/api/bild/([1-6])', pfad)
            if bild:
                nummer = int(bild.group(1))
                query = parse_qs(url.query)
                try:
                    hoehe = float(query.get('h', ['1.0'])[0])
                    if not .3 <= hoehe <= 1.5:
                        raise ValueError()
                    schritte = int(query.get('schritte', [str(self.server.schritte_pro_bild)])[0])
                    if not 0 <= schritte <= 100:
                        raise ValueError()
                except ValueError:
                    self.antwort('Ungültige Stufenhöhe oder Schrittzahl.'.encode('utf-8'),
                                 'text/plain; charset=utf-8', 400)
                    return
                sitzung, cookie_neu = self.session_id()
                eintrag = self.zustand(sitzung, nummer)
                with eintrag['sperre']:
                    sim = eintrag['simulation']
                    neue_hoehe = sim.par.with_h(hoehe).h
                    if abs(neue_hoehe-sim.par.h) > 1e-9:
                        sim.change_h(neue_hoehe)
                    if schritte and sim.t < sim.par.t_end:
                        sim.step(schritte)
                    from s08_einzelseite import bild_als_png
                    # Matplotlib ist nicht threadsicher; die Darstellung zentral sperren.
                    with self.server.zeichensperre:
                        daten = bild_als_png(sim, nummer)
                    info = sim.diagnostics()
                    status = {'hoehe':sim.par.h, 'zeit':sim.t, 'schritte':sim.n,
                              'massenbilanzfehler':info['mass_error'],
                              'druckresiduum':info['pressure_residual']}
                    self.antwort(daten, 'image/png', sitzung=cookie_neu,
                                 zusaetzlich={'X-CFD-Status':json.dumps(status,
                                                              ensure_ascii=True,
                                                              separators=(',', ':'))})
                return
            self.antwort('Seite nicht gefunden.'.encode('utf-8'),
                         'text/plain; charset=utf-8', 404)

        def do_POST(self):
            treffer = re.fullmatch(r'/api/neustart/([1-6])', urlsplit(self.path).path)
            if not treffer:
                self.antwort(b'Nicht gefunden.', 'text/plain; charset=utf-8', 404)
                return
            try:
                laenge = int(self.headers.get('Content-Length', '0'))
                if not 0 <= laenge <= 1024:
                    raise ValueError()
                daten = json.loads(self.rfile.read(laenge) or b'{}')
                hoehe = float(daten.get('h', 1.0))
                if not .3 <= hoehe <= 1.5:
                    raise ValueError()
            except (ValueError, TypeError, json.JSONDecodeError):
                self.antwort(b'Ungueltige Eingabe.', 'text/plain; charset=utf-8', 400)
                return
            sitzung, cookie_neu = self.session_id()
            eintrag = self.zustand(sitzung, int(treffer.group(1)))
            with eintrag['sperre']:
                eintrag['simulation'].change_h(hoehe)
            self.antwort(json.dumps({'meldung':'Simulation neu gestartet',
                                     'hoehe':eintrag['simulation'].par.h},
                                    ensure_ascii=False).encode('utf-8'),
                         'application/json; charset=utf-8', sitzung=cookie_neu)

    server = PraesentationsServer((host, port), Anfrage)
    server.zustaende = {}
    server.zustandssperre = Lock()
    server.zeichensperre = Lock()
    server.druckloeser = druckloeser
    server.schritte_pro_bild = schritte_pro_bild
    return server


def starten(host='127.0.0.1', port=8765, druckloeser='lu',
             schritte_pro_bild=8, browser_oeffnen=True):
    server = server_erzeugen(host, port, druckloeser, schritte_pro_bild)
    adresse = f'http://{host}:{server.server_port}/'
    print(f'Sechs getrennte CFD-Präsentationsseiten: {adresse}')
    print('Jedes Diagramm besitzt einen eigenen Stufenhöhenregler und eine eigene Zeitanimation.')
    print('Mit Strg+C lässt sich der Server beenden.')
    if browser_oeffnen:
        webbrowser.open(adresse)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nDer Präsentationsserver wurde beendet.')
    finally:
        server.server_close()
