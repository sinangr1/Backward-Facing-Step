# CFD-Präsentation: sechs getrennte Live-Seiten

## Ziel

Strömung an einer **rückwärtsgerichteten Stufe** gemäß den bereitgestellten Vorlesungsabbildungen. Die **sechs Ergebnisse erscheinen nicht nebeneinander**, sondern werden auf **sechs voneinander unabhängigen Seiten** gezeigt. Jede Seite besitzt ihren eigenen Stufenhöhenregler `h`, eine zeitabhängige Neuberechnung sowie die Schaltflächen **Pause**, **Fortsetzen**, **Neu starten** und **Vollbild**. Alle sichtbaren Erläuterungen sind deutsch.

## 1. Präsentation im Browser starten (empfohlen)

Nach dem Entpacken im Projektverzeichnis:

```bash
python -m pip install -r requirements.txt
python 00_pipeline.py
```

Die lokale Startseite öffnet sich unter **http://127.0.0.1:8765/**. Wählen Sie dort genau eine der sechs eigenständigen Auswertungen aus:

| Seite | Browser-Adresse | Eigenständiges Python-Modul | Jupyter-Notebook |
|---|---|---|---|
| 1 – Geschwindigkeitsbetrag | `/seite/1` | `diagramm_01_geschwindigkeitsbetrag.py` | `01_geschwindigkeitsbetrag.ipynb` |
| 2 – Druckverteilung | `/seite/2` | `diagramm_02_druckverteilung.py` | `02_druckverteilung.ipynb` |
| 3 – Stromlinien | `/seite/3` | `diagramm_03_stromlinien.py` | `03_stromlinien.ipynb` |
| 4 – Wandschubspannung | `/seite/4` | `diagramm_04_wandschubspannung.py` | `04_wandschubspannung.ipynb` |
| 5 – Wirbelstärke | `/seite/5` | `diagramm_05_wirbelstaerke.py` | `05_wirbelstaerke.ipynb` |
| 6 – Druckverlauf | `/seite/6` | `diagramm_06_druckverlauf.py` | `06_druckverlauf.ipynb` |

Die Seiten lassen sich unabhängig öffnen. Jede Seitenadresse besitzt einen eigenen Simulationszustand im selben Browser: Wenn Sie etwa die Druckverteilung verändern, verändert das nicht die Simulation auf der Stromlinienseite. Die Navigation **Vorherige Seite**, **Startseite** und **Nächste Seite** erleichtert den Einzelvortrag. **Vollbild** blendet Browserleisten auf vielen Systemen aus.

Die Web-Präsentation verwendet ausschließlich den eingebauten Python-Webserver sowie die für CFD ohnehin erforderlichen NumPy-, SciPy- und Matplotlib-Pakete: Es wird keine externe Webplattform benötigt. Der Server ist nur lokal erreichbar.

## 2. Einzelne Live-Diagramme ohne Browser starten

Sie können jede Abbildung auch direkt in einem eigenen Matplotlib-Fenster vorführen:

```bash
python 00_pipeline.py --seite 1
python 00_pipeline.py --seite 2
python 00_pipeline.py --seite 3
python 00_pipeline.py --seite 4
python 00_pipeline.py --seite 5
python 00_pipeline.py --seite 6
```

Alternativ starten die sechs Dateien `diagramm_01_...py` bis `diagramm_06_...py` jeweils nur ihr eigenes animiertes Fenster. Auf jeder Seite wird die Stufenhöhe mit dem Regler eingestellt. Auch im Matplotlib-Fenster stehen **Pause** und **Neu starten** zur Verfügung.

## 3. Sechs einzelne Jupyter-Notebooks

Mit `jupyter lab` starten und pro Thema ein eigenes Notebook öffnen. **Jedes Notebook enthält genau ein Live-Diagramm**, alle mit eigenem Stufenhöhenregler. Das Backend `%matplotlib widget` benötigt `ipympl` aus `requirements.txt`. Die Notebooks öffnen jeweils nur ihr einzelnes Diagramm; die früheren sechs gemeinsamen Unterdiagramme werden nicht aufgerufen.

Die Datei `00_startseite.ipynb` verlinkt die sechs Einzel-Notebooks.

## 4. Animierte GIF-Datei für eine einzelne Seite speichern

```bash
python 00_pipeline.py --seite 3 --gif ergebnisse/stromlinien.gif --bilder 30
python 00_pipeline.py --seite 5 --gif ergebnisse/wirbelstaerke_h.gif --hoehenvariation --bilder 24
```

**Hinweis:** Ein GIF zeigt eine aufgezeichnete Animation, während Browserseiten, Python-Fenster und Notebooks eine **laufende Neuberechnung** erlauben. Der `h`-Regler ist im GIF nicht bedienbar. Im Ordner `ergebnisse/einzelanimationen/` liegen sechs Präsentations-GIFs.

## 5. Physikalische Grundlagen

Das numerische Modell ist ein zweidimensionaler, inkompressibler Navier–Stokes-Löser mit versetztem **MAC-Gitter**. Der Impulsschritt berechnet die Zwischengeschwindigkeiten `F` und `G`. Die Druck-Poisson-Gleichung erzwingt über eine Projektion annähernd die Divergenzfreiheit. Als Drucklöser steht die schnelle **LU-Zerlegung** oder das in der Vorlesung genannte **SOR-Verfahren** zur Wahl (`--druckloeser sor`).

Vorlesungsparameter: `imax = 100`, `jmax = 20`, `xlength = 10`, `ylength = 2`, `dt ≤ 0,05`, `tau = 0,5`, `alpha = 0,9`, `eps = 0,001`, `omg = 1,7`, `itermax = 500`, `Re = 100`. Links gilt die Einströmung `u = 1`, `v = 0` nur im offenen Kanalbereich; rechts freier Auslass mit Druckreferenz; an den Wänden wird die Haftbedingung verwendet. Die Anfangswerte aus den bereitgestellten Abbildungen werden berücksichtigt.

Mit `h` verändern sich die Fluidmaske, die offene Einlasshöhe und die Diskretisierung der Druckgleichung. Beim Ändern werden die Poisson-Matrix und das gesamte Geschwindigkeits- und Druckfeld neu berechnet. Die Simulation beginnt dann bei `t = 0`.

Die Strömungsfelder und Diagramme stellen eine numerische Demonstration dar, keine experimentell validierte Referenz. Bei SOR reichen 500 Iterationen nicht in jedem Zeitschritt für die Toleranz `eps` aus; das Druckresiduum wird deshalb ausgegeben. Die Wandschubspannung ist an den Wänden definiert und wird als farbige Wandlinie dargestellt.

## 6. Tests

```bash
python -m pytest -q
```

Die Tests überprüfen unter anderem die Neuberechnung bei geänderter Stufenhöhe, die Massenbilanz, die sechs einzelnen Darstellungen sowie die sechs getrennten Browser-Adressen und ihre Zustandsführung.

## Projektstruktur

- `00_pipeline.py` – Hauptpipeline: Browserseiten, einzelne Matplotlib-Fenster oder Einzel-GIFs
- `s01_parameter.py` bis `s07_auswertung.py` – CFD-Modell, Geometrie, Randbedingungen, Impuls, Druck, Simulation, Auswertung
- `s08_einzelseite.py` – eine einzelne animierte Matplotlib-Auswertung
- `s09_webseiten.py` – lokaler Server für sechs getrennte Präsentationsseiten
- `diagramm_01_*.py` bis `diagramm_06_*.py` – sechs unabhängige Zeichenmodule
- `webseite/` – deutschsprachige Browseroberfläche
- `01_*.ipynb` bis `06_*.ipynb` – sechs unabhängige interaktive Notebook-Seiten
- `ergebnisse/einzelanimationen/` – sechs separate Animationsdateien
- `tests/` – numerische und funktionale Tests

**Quellenbasis:** bereitgestellte Folienabbildungen und ursprüngliche Jupyter-Notebooks. Eine vollständige Vorlesungs-PDF lag nicht vor; hier wird keine zusätzliche PDF-Quelle unterstellt.
