# PorCuanto V14 — Identificación visual + comparables web

Flujo principal:
1. Foto del producto.
2. Lectura local de código de barras y OCR.
3. Búsqueda visual web mediante Google Lens como fallback sin API oficial.
4. OpenAI Vision opcional para afinar marca/modelo/EAN/ASIN cuando está configurado.
5. Búsqueda pública de referencias y comparables.
6. Comparación con mercados Amazon/eBay cuando están configurados.
7. Cálculo de beneficio, ROI y máximo de compra.

La búsqueda visual sin API depende de que Google mantenga disponible su endpoint web de Lens; si cambia, la app conserva OCR, códigos, búsqueda web y las APIs opcionales.
