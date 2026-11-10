/* Interaktive Steuerung einer einzigen Live-CFD-Präsentationsseite. */
'use strict';
const seite = Number(document.body.dataset.seite);
const regler = document.getElementById('hoehe');
const hoehetext = document.getElementById('hoehetext');
const bild = document.getElementById('livebild');
const status = document.getElementById('status');
const ladehinweis = document.getElementById('ladehinweis');
const pausetaste = document.getElementById('pause');
const neustarttaste = document.getElementById('neustart');
const vollbildtaste = document.getElementById('vollbild');
let laeuft = true;
let beschaeftigt = false;
let vorgemerkt = false;
let bildadresse = null;
let folgeaufruf = null;

function formatZahl(wert, stellen = 2) {
  return Number(wert).toLocaleString('de-DE', {minimumFractionDigits: stellen,maximumFractionDigits: stellen});
}
function hoeheAktualisieren() { hoehetext.textContent = formatZahl(regler.value,1); }
function naechsterAufruf() {
  clearTimeout(folgeaufruf);
  if (laeuft) folgeaufruf = setTimeout(() => bildLaden(false), 230);
}
async function bildLaden(sofort = false) {
  clearTimeout(folgeaufruf);
  if (!laeuft && !sofort) return;
  if (beschaeftigt) { vorgemerkt = true; return; }
  beschaeftigt = true;
  const angefragteHoehe = Number(regler.value);
  const schritte = laeuft ? 8 : 0;
  try {
    const antwort = await fetch(`/api/bild/${seite}?h=${angefragteHoehe}&schritte=${schritte}`, {cache:'no-store'});
    if (!antwort.ok) throw new Error('Berechnung nicht verfügbar (' + antwort.status + ')');
    const info = JSON.parse(antwort.headers.get('X-CFD-Status') || '{}');
    const png = await antwort.blob();
    if (Math.abs(angefragteHoehe - Number(regler.value)) > .001) return;
    const neueAdresse = URL.createObjectURL(png);
    bild.onload = () => {
      if (bildadresse) URL.revokeObjectURL(bildadresse);
      bildadresse = neueAdresse;
      ladehinweis.hidden = true;
    };
    bild.src = neueAdresse;
    status.textContent = `Stufenhöhe h = ${formatZahl(info.hoehe)}  ·  Zeit t = ${formatZahl(info.zeit,3)}  ·  Zeitschritte = ${info.schritte}  ·  Massenbilanzfehler = ${Number(info.massenbilanzfehler).toExponential(2)}`;
  } catch (fehler) {
    ladehinweis.hidden = false;
    ladehinweis.textContent = 'Berechnung fehlgeschlagen: ' + fehler.message;
    status.textContent = 'Bitte prüfen Sie, ob das lokale Python-Programm noch ausgeführt wird.';
  } finally {
    beschaeftigt = false;
    if (vorgemerkt) { vorgemerkt = false; bildLaden(true); }
    else naechsterAufruf();
  }
}
regler.addEventListener('input', hoeheAktualisieren);
regler.addEventListener('change', () => {
  status.textContent = 'Neue Stufenhöhe: Geometrie und Druckmatrix werden neu berechnet …';
  ladehinweis.hidden = false;
  bildLaden(true);
});
pausetaste.addEventListener('click', () => {
  laeuft = !laeuft;
  pausetaste.textContent = laeuft ? 'Pause' : 'Fortsetzen';
  if (laeuft) bildLaden(true);
  else { clearTimeout(folgeaufruf); status.textContent += '  ·  Angehalten'; }
});
neustarttaste.addEventListener('click', async () => {
  clearTimeout(folgeaufruf);
  try {
    const antwort = await fetch(`/api/neustart/${seite}`, {
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({h:Number(regler.value)})
    });
    if (!antwort.ok) throw new Error('Neustart fehlgeschlagen');
    ladehinweis.hidden = false;
    status.textContent = 'Die Simulation wird mit den Anfangsbedingungen neu gestartet.';
    bildLaden(true);
  } catch (fehler) { status.textContent = fehler.message; }
});
vollbildtaste.addEventListener('click', async () => {
  if (!document.fullscreenElement) await document.documentElement.requestFullscreen();
  else await document.exitFullscreen();
});
hoeheAktualisieren();
bildLaden(true);
