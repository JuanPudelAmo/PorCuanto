# PorCuanto V10 — Guía de conexión de APIs

## Importante

PorCuanto V10 **no obliga a conectar ninguna API**. Sin APIs, la aplicación puede usar la búsqueda pública de Internet y enlaces de mercado.

Las APIs son opcionales y añaden datos directos/estructurados.

---

## 1. OpenAI — análisis de fotos

1. Entra en la plataforma de OpenAI.
2. Crea/inicia sesión en tu cuenta de API.
3. Crea una API key.
4. En el servidor de PorCuanto, abre `.env`.
5. Añade:

`OPENAI_API_KEY=tu_clave`

6. Reinicia PorCuanto.
7. Abre **⚙️ Conectar APIs → Comprobar conexiones**.

OpenAI documenta la creación de API keys y recomienda mantenerlas como secretos y cargarlas en el servidor, no en el código del navegador.

**Facturación:** ChatGPT y la plataforma API tienen facturación separada. Una suscripción de ChatGPT no incluye automáticamente saldo de API.

---

## 2. Keepa — precios e historial de Amazon

1. Crea/inicia sesión en Keepa.
2. Entra en la sección API.
3. Contrata/activa el plan API que quieras utilizar.
4. Copia la API key.
5. En `.env`:

`KEEPA_API_KEY=tu_clave`

6. Reinicia PorCuanto.
7. Comprueba la conexión desde la aplicación.

Keepa proporciona datos de Amazon como historial de precios, ofertas y vendedores. Sus consultas utilizan tokens.

---

## 3. eBay — comparables

1. Crea/inicia sesión en eBay Developers.
2. Entra en **Application Keys**.
3. Crea/selecciona tu aplicación.
4. Usa las credenciales de **Production** cuando quieras consultar datos reales.
5. Copia:
   - App ID = Client ID
   - Cert ID = Client Secret
6. En `.env`:

`EBAY_CLIENT_ID=...`
`EBAY_CLIENT_SECRET=...`

7. Reinicia PorCuanto.
8. Pulsa **Comprobar conexiones**.

Para el Browse API, eBay utiliza OAuth y las búsquedas pueden utilizar un Application access token. El client secret debe mantenerse secreto.

---

## 4. Seguridad

Nunca pongas estas claves en:
- HTML
- JavaScript del navegador
- repositorios públicos
- capturas de pantalla
- anuncios

Deben permanecer en el servidor/variables de entorno.

---

## 5. Si no quieres pagar ninguna API

No conectes nada.

Utiliza:

**📷 Foto/EAN → identificación → búsqueda pública → comparables → cálculo**

La app seguirá siendo útil, pero los datos pueden ser menos completos que con APIs especializadas.

---

## 6. Configuración recomendada

Para una instalación personal:

- OpenAI: opcional pero recomendable para fotos.
- Keepa: recomendable si quieres datos Amazon estructurados.
- eBay: recomendable para comparables.
- Búsqueda web: siempre activa como complemento.

