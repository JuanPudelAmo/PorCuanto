# PorCuanto V26 — análisis rápido y visible

## Cambios principales
- El análisis ya no queda bloqueado esperando Google Lens.
- La búsqueda visual se ejecuta en segundo plano después de mostrar el resultado principal.
- La identificación por EAN/UPC/GTIN tiene tiempos máximos cortos y una sola búsqueda web combinada.
- Los mercados con Keepa se consultan en paralelo, en vez de uno detrás de otro.
- Las búsquedas web públicas se ejecutan en paralelo y con timeout corto.
- El overlay grande «Analizando producto…» sigue visible durante las operaciones críticas y después desaparece en cuanto ya hay resultado.
- El botón muestra «⏳ ANALIZANDO…» y queda bloqueado durante el proceso.
- Si la búsqueda visual tarda o falla, no bloquea el resultado.

## Objetivo
Evitar que PorCuanto parezca congelado o se quede indefinidamente en «Analizando».

## Instalación
Versión plana: sube todos los archivos del ZIP a la raíz del repositorio de GitHub y sobrescribe los anteriores. Render desplegará el cambio si está conectado al repositorio.
