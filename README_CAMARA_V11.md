# PorCuanto V11 — Cámara corregida

La cámara ahora tiene tres vías:
1. Cámara web trasera mediante `getUserMedia()` cuando la página está en un contexto seguro.
2. Fallback de cámara nativa del teléfono mediante `<input type=file capture=environment>`.
3. Galería normal.

Además muestra errores específicos de permisos, cámara ocupada, cámara inexistente y contexto no seguro.

Nota: los navegadores restringen `getUserMedia()` a contextos seguros (HTTPS o localhost). En Android, si se abre el HTML directamente o desde un entorno que no concede permisos, usa **CÁMARA DEL TELÉFONO**.
