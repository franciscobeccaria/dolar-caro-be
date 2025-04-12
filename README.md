# ¿El dólar está caro en Argentina? - Backend API

Backend en Python para el proyecto "¿El dólar está caro en Argentina?". Este sistema permite comparar precios de productos entre Argentina y otros países utilizando el tipo de cambio del dólar blue, para determinar si los productos son caros o baratos en Argentina en comparación con lugares como EE.UU., Chile o Brasil.

## Características

- **Diseño Orientado a Objetos**: Modelos para Product, Country, Price, Source, etc.
- **Scraping Avanzado**: Obtiene precios de Nike, Adidas y más utilizando Playwright con técnicas anti-bloqueo
- **Almacenamiento en Base de Datos**: Guarda todos los datos en SQLite usando SQLAlchemy ORM
- **Datos Históricos**: Seguimiento de cambios de precios a lo largo del tiempo
- **Interfaz CLI**: Ejecuta scrapers y gestiona datos desde la línea de comandos
- **API REST**: Accede a los datos de precios mediante endpoints FastAPI
- **Conversión ARS/USD**: Utiliza [DolarApi.com](https://dolarapi.com/) para obtener la cotización del dólar blue

## Estructura del Proyecto

```
dolar_caro_backend/
├── models.py           # Modelos SQLAlchemy ORM
├── db_manager.py       # Operaciones de base de datos
├── scrapers/           # Módulos de scraping
│   ├── __init__.py
│   ├── base_scraper.py # Clase base para scrapers
│   ├── nike_scraper.py # Scraper específico para Nike
│   └── adidas_scraper.py # Scraper específico para Adidas
├── services.py         # Lógica de negocio
├── api.py              # Endpoints FastAPI
├── cli.py              # Interfaz de línea de comandos
├── utils.py            # Funciones de utilidad
├── db/                 # Archivos de base de datos
└── data/               # Almacenamiento de datos JSON
```

## Endpoints disponibles

- `/nike` → Devuelve precios de Nike Air Force One en AR y US
- `/adidas-jersey` → Devuelve precios de la camiseta aniversario de Argentina de Adidas en AR y US
- `/all` → Devuelve todos los productos juntos
- `/history/{endpoint}` → Devuelve datos históricos para un endpoint específico (nike, adidas-jersey, all)

## Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/franciscobeccaria/dolar-caro-be.git
cd dolar-caro-be
```

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

3. Instalar los navegadores necesarios para Playwright:

```bash
python -m playwright install chromium
```

4. Configurar la base de datos:

```bash
python cli.py setup
```

## Uso

### Interfaz de Línea de Comandos

El proyecto incluye una CLI para ejecutar scrapers y gestionar datos:

```bash
# Configurar la base de datos con datos iniciales
python cli.py setup

# Obtener precios de Nike
python cli.py nike

# Obtener precios de Adidas
python cli.py adidas

# Obtener todos los precios
python cli.py all

# Habilitar modo de depuración (toma capturas de pantalla)
python cli.py all --debug

# No guardar resultados en JSON
python cli.py all --no-json
```

### API

Iniciar el servidor API:

```bash
python api.py
```

O con uvicorn:

```bash
uvicorn api:app --reload
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
  "product": "Nike Air Force 1",
  "us_price": 110,
  "ar_price": 199999,
  "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
  "url_ar": "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
  "exchange_rate": 1375.0,
  "ar_price_usd": 145.45,
  "timestamp": "2025-04-12T13:31:48.869844"
}
```

Ejemplo de respuesta JSON para el endpoint `/history/nike`:

```json
{
  "endpoint": "nike",
  "count": 2,
  "history": [
    {
      "product": "Nike Air Force 1",
      "us_price": 110,
      "ar_price": 199999,
      "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
      "url_ar": "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
      "exchange_rate": 1375.0,
      "ar_price_usd": 145.45,
      "timestamp": "2025-04-12T13:31:48.869844"
    },
    {
      "product": "Nike Air Force 1",
      "us_price": 110,
      "ar_price": 189999,
      "url_us": "https://www.nike.com/t/air-force-1-07-mens-shoes-5QFp5Z/CW2288-111",
      "url_ar": "https://www.nike.com.ar/nike-air-force-1--07-cw2288-111/p",
      "exchange_rate": 1350.0,
      "ar_price_usd": 140.74,
      "timestamp": "2025-04-11T10:30:00.123456"
    }
  ]
}
```

## Estructura de la Base de Datos

El proyecto utiliza SQLAlchemy ORM con los siguientes modelos:

- **Country**: Representa un país con su moneda
- **Category**: Categorías de productos (por ejemplo, Calzado, Ropa deportiva)
- **Product**: Productos para los que se rastrean precios
- **Source**: De dónde provienen los datos de precios (scraping, API, manual)
- **Price**: Registros de precios individuales con marca de tiempo y tipo de cambio
- **ExchangeRate**: Registros de tipos de cambio
- **ScraperRun**: Registros de ejecuciones de scrapers

## Añadir Nuevos Scrapers

Para añadir un nuevo scraper:

1. Crear una nueva clase scraper en el directorio `scrapers`, heredando de `BaseScraper`
2. Implementar el método `scrape()`
3. Añadir el scraper a la clase `PriceService` en `services.py`
4. Añadir un nuevo comando a la CLI en `cli.py`
5. Añadir un nuevo endpoint a la API en `api.py`

## Notas

- Los precios se actualizan manualmente mediante la CLI o automáticamente mediante un cron job
- Si el scraping falla, se utilizan valores predeterminados configurados en cada scraper
- La API utiliza la cotización del dólar blue de Argentina a través de DolarApi
- Los datos históricos se almacenan en archivos JSON en el directorio `data/`
- Para cada endpoint se guarda una copia del último resultado en `latest.json`

## Licencia

MIT
