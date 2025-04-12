# ¿El dólar está caro en Argentina? - Backend API

Backend simple en Python para el proyecto "¿El dólar está caro en Argentina?". Esta API permite scrapear precios de productos desde distintas páginas y exponerlos mediante endpoints REST para ser consumidos por un frontend en Next.js.

## Características

- Scraping avanzado de precios actuales desde Nike y Adidas Argentina/EE.UU. con técnicas anti-bloqueo
- Endpoints REST para acceder a los datos
- Conversión ARS/USD utilizando [DolarApi.com](https://dolarapi.com/)
- Cache de datos para evitar múltiples scraping
- Almacenamiento histórico de precios para análisis de tendencias

## Endpoints disponibles

- `/nike` → Devuelve precios de Nike Air Force One en AR y US
- `/adidas-jersey` → Devuelve precios de la camiseta aniversario de Argentina de Adidas en AR y US
- `/all` → Devuelve todos los productos juntos
- `/history/{endpoint}` → Devuelve datos históricos para un endpoint específico (nike, adidas-jersey, all)

## Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio o descargar los archivos

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

3. Instalar los navegadores necesarios para Playwright:

```bash
python -m playwright install chromium
```

## Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`

## Documentación de la API

FastAPI genera automáticamente la documentación de la API. Puedes acceder a ella en:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Formato de respuesta

Ejemplo de respuesta JSON para el endpoint `/nike`:

```json
{
  "producto": "Nike Air Force One",
  "precio_ars": 250000,
  "precio_usd": 110,
  "precio_ars_usd": 200,
  "url_ar": "https://www.nike.com.ar/calzado/zapatillas/air-force-1",
  "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
  "dolar_blue": 1250
}
```

Ejemplo de respuesta JSON para el endpoint `/history/nike`:

```json
{
  "endpoint": "nike",
  "count": 2,
  "history": [
    {
      "producto": "Nike Air Force One",
      "precio_ars": 199999,
      "precio_usd": 110,
      "precio_ars_usd": 145.45,
      "url_ar": "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
      "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
      "dolar_blue": 1375,
      "timestamp": "2025-04-12T01:45:00.123456"
    },
    {
      "producto": "Nike Air Force One",
      "precio_ars": 189999,
      "precio_usd": 110,
      "precio_ars_usd": 140.74,
      "url_ar": "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
      "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
      "dolar_blue": 1350,
      "timestamp": "2025-04-11T10:30:00.123456"
    }
  ]
}
```

## Notas

- Los precios se actualizan automáticamente cada hora
- Si el scraping falla, se utilizan valores predeterminados
- La API utiliza la cotización del dólar blue de Argentina
- Los datos históricos se almacenan en archivos JSON en el directorio `data/`
- Para cada endpoint se guarda una copia del último resultado en `latest.json`
