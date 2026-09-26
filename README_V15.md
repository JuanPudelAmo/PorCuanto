# PorCuanto V15 — identificación visual + comparación web

## IMPORTANTE: por qué aparecía “Failed to fetch”
PorCuanto necesita ejecutar `app.py` como servidor FastAPI. Si se abre `static/index.html` directamente desde el administrador de archivos del móvil (`file://...`), el navegador no tiene ningún `/api/...` al que conectarse y muestra `Failed to fetch`.

### PC Windows
Ejecuta `start_windows.bat`. Se instalarán las dependencias, se arrancará el servidor y se abrirá:
`http://localhost:8000`

### Mac / Linux
Ejecuta `./start_linux_mac.sh`.

### Android con Termux
Copia la carpeta al teléfono, instala Termux y ejecuta `./start_android_termux.sh`. Después abre `http://127.0.0.1:8000` en el navegador.

## Flujo V15
1. Foto.
2. OCR + código de barras local.
3. Búsqueda visual en Google Lens desde el servidor.
4. Identificación por OpenAI opcional.
5. Búsqueda pública de comparables.
6. Amazon/Keepa y eBay si están configurados.
7. Beneficio, ROI y máximo de compra.

La interfaz ahora detecta específicamente cuando no existe conexión con el servidor y muestra la solución en lugar de `Failed to fetch`.
