# PorCuanto V17 — despliegue gratuito en Render

1. Sube el contenido de esta carpeta a un repositorio GitHub público.
2. En Render: New → Web Service → conecta GitHub → selecciona el repositorio.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Plan: Free.
6. No subas `.env` ni claves API a GitHub. Si las necesitas, añádelas en Render → Environment.

`render.yaml` ya contiene esta configuración para el despliegue automático.
