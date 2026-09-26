# PorCuanto V25

## Cambios principales
- **Análisis visible:** al pulsar ANALIZAR OPORTUNIDAD aparece una pantalla grande centrada con spinner y 4 pasos: detectar → identificar → comparar → calcular.
- **Botón bloqueado durante el análisis:** cambia a `⏳ ANALIZANDO…` para evitar dobles pulsaciones.
- **EAN/UPC/GTIN mejorado:** primero intenta resolver el código con una base de productos (UPCitemdb) y después amplía la búsqueda pública con varias consultas.
- **No muestra el EAN como si fuera el nombre del producto** cuando no se ha podido identificar.
- **Precios de la base de producto:** si están disponibles, se incorporan a la referencia de mercado.
- **Escáner de código mejorado:** añade fallback ZXing cuando el navegador no dispone de BarcodeDetector.
- **Comparación web ampliada:** combina título, marca, modelo y EAN para buscar referencias.
- Proyecto **plano, sin carpetas**, preparado para subir todos los archivos directamente al repositorio de GitHub.

## API de código de barras
V25 usa el endpoint gratuito de consulta de UPCitemdb sin exigir una clave al usuario. El servicio tiene límites de uso; si se alcanza el límite, PorCuanto continúa con búsqueda web y otras fuentes configuradas.

## Deploy Render
Mantén:
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
