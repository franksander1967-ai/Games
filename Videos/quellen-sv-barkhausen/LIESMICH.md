# SV Barkhausen – Werbespot (Quellen)

Fertiges Video: `../SV_Barkhausen_Werbespot_9x16.mp4` (30 s, 1080×1920, 60 fps).

- `video.html` – Animation aller 7 Szenen (`render(t)` zeichnet das Bild zur Zeit t)
- `objects.js` – Gewehr, Schützenhut, Königskette, Pokal als SVG
- `audio.py` – synthetisierte Musik und Soundeffekte → `score.wav`
- `render.js` – rendert `video.html` Bild für Bild per Playwright + ffmpeg
- `logo.html` – Wappen mit neu gesetzter Ringschrift → `logo_2x.png`

Neu bauen:
```
python3 audio.py
NODE_PATH=$(npm root -g) node render.js 60 v60.mp4
ffmpeg -i v60.mp4 -i score.wav -filter_complex "[1:a]volume=-7.4dB,alimiter=limit=0.8:level=false[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -shortest SV_Barkhausen_Werbespot_9x16.mp4
```
