# PorCuanto V19 — European Arbitrage Scanner

V7 está enfocada a arbitraje europeo.

## Funciones
- Escáner de códigos de barras EAN/UPC/GTIN con cámara cuando el navegador soporta `BarcodeDetector`.
- Foto del producto.
- ASIN y búsqueda manual.
- Mercados Amazon: ES, DE, FR, IT, UK, NL, BE, PL, SE, IE y TR.
- Keepa directo para ES, DE, FR, IT y UK en esta integración, según los dominios disponibles en su API.
- Los demás mercados quedan preparados para búsqueda web directa.
- Comparación de Amazon + eBay.
- Beneficio, margen, ROI y precio máximo de compra.

## Keepa
Configura `KEEPA_API_KEY`. La API de Keepa usa un sistema de tokens y requiere una suscripción/API key. Consulta su documentación oficial para precios y planes.

## eBay
Configura `EBAY_CLIENT_ID` y `EBAY_CLIENT_SECRET`.

## OpenAI
`OPENAI_API_KEY` solo es necesaria para identificar un producto a partir de una foto.

## Nota importante
Comparar un precio de venta entre países no significa que ese producto pueda venderse automáticamente en todos los mercados. Antes de comprar para arbitraje hay que comprobar elegibilidad de la cuenta, categoría, restricciones, IVA/IGIC, cumplimiento de producto, logística y costes reales.


## Productos sin código de barras / mercadillos

V7 no exige EAN, UPC ni ASIN. Puedes fotografiar un producto antiguo, usado, de coleccionismo o de mercadillo y la app utiliza la identificación visual y varias pistas (marca, modelo, variante y texto) para generar búsquedas.

Si configuras `SERPAPI_KEY`, añade resultados web de Google como complemento para encontrar anuncios y páginas donde aparezca el artículo.

eBay Browse también permite buscar por imagen, GTIN y palabras clave; sin embargo, `searchByImage` no está disponible en todos los marketplaces. Por eso V7 no depende exclusivamente de esa función.


## Cámara y escáner (V7.1)

La cámara web del navegador requiere un contexto seguro: **HTTPS o localhost**. Si abres `index.html` directamente desde el ZIP/gestor de archivos, algunos navegadores móviles no concederán acceso a la cámara. `getUserMedia()` está sujeto a permisos y seguridad del navegador.

V7.1 incluye:
- botón de cámara trasera mediante `getUserMedia()`;
- captura de foto desde la cámara;
- lector automático mediante `BarcodeDetector` cuando el navegador lo soporte;
- alternativa de fotografía/galería cuando `BarcodeDetector` no esté disponible;
- EAN/UPC manual como último recurso.

Para usar la cámara web desde un ordenador, ejecuta el servidor y abre `http://localhost:8000`. Para usarlo públicamente desde el móvil, publícalo bajo HTTPS.


## V7 Fast Fix

Esta edición reduce las esperas:
- comprime la foto en el móvil antes de enviarla;
- muestra vista previa y estado inmediatamente;
- reduce los timeouts;
- consulta los mercados Keepa en paralelo en lugar de uno detrás de otro;
- si hay EAN/ASIN, evita depender de la visión para encontrar el producto;
- si no hay código, usa la foto para identificarlo.

Keepa cobra tokens por consultas: una búsqueda de productos puede costar 10 tokens por página y una consulta individual por ASIN 1 token, por lo que no conviene lanzar búsquedas innecesarias a todos los mercados. 


## V8 — flujo progresivo rápido

El análisis se divide en tres fases:
1. Identificación del producto.
2. Consulta de mercados.
3. Cálculo de oportunidad.

Esto evita que la interfaz parezca bloqueada mientras se consultan todas las fuentes. Los mercados se pueden seleccionar para reducir tiempo y consumo de tokens. Keepa cobra 1 token por ASIN y 10 tokens por página de búsqueda de productos, según su documentación actual. citeturn0search0turn0search7


# V9 — Desarrollo

V9 añade:
- cámara en vivo con cámara trasera;
- captura directa y galería;
- modo sin código para mercadillos;
- identificación separada de la búsqueda de precios;
- mercados Amazon consultados después de identificar;
- búsqueda pública web secundaria y no bloqueante;
- resultado progresivo;
- cálculo de beneficio, ROI y máximo de compra;
- selección de mercados para controlar velocidad y consumo.

La API de Keepa permite consultar productos por ASIN/product code y también búsquedas por palabra; además, soporta peticiones paralelas. citeturn0search0turn0search9
eBay Browse permite búsquedas por palabra, GTIN e imagen, aunque la disponibilidad de searchByImage depende del marketplace. citeturn0search1turn0search3


## V10 — APIs opcionales

V10 funciona sin APIs. Incluye una pantalla **Conectar APIs** con estado y guía paso a paso para OpenAI, Keepa y eBay.

OpenAI: la API usa API keys y debe mantenerse en el servidor. La facturación de la API es independiente de la suscripción de ChatGPT. citeturn1search2turn1search0

Keepa: se obtiene una API key desde su sección API y sus solicitudes utilizan tokens. citeturn0search4

eBay: las credenciales se obtienen desde Application Keys y consisten en Client ID/App ID y Client Secret/Cert ID. El Browse API puede utilizar Application access tokens mediante client credentials. citeturn0search0turn0search9

La cámara usa getUserMedia en contexto seguro; el detector de códigos de barras nativo no está disponible en todos los navegadores, por lo que la app mantiene foto/entrada manual como alternativa. citeturn0search1turn0search13

### V13 — análisis de foto sin API
La aplicación incorpora lectura local de códigos de barras cuando el navegador lo soporta y OCR local mediante Tesseract.js para leer marca/modelo/texto de la etiqueta. Después usa esos datos para realizar la búsqueda pública de referencias, sin necesitar una clave de OpenAI para ese flujo. La precisión depende de que el producto/etiqueta sea legible.


## V18 — subida sencilla a GitHub
Los archivos web (`index.html`, `icon.svg`, `manifest.webmanifest`, `sw.js`) están en la raíz. No necesitas subir ninguna carpeta `static`.
