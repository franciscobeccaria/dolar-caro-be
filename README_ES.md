# ¿El dólar está caro en Argentina? - Guía para Desarrolladores Frontend

## Visión General del Proyecto

Este proyecto es un backend para comparar precios de productos entre Argentina y otros países (principalmente EE.UU.), utilizando el tipo de cambio del dólar blue. El objetivo es determinar si los productos son caros o baratos en Argentina comparados con otros países.

El sistema:

1. Obtiene precios de sitios web como Nike y Adidas usando web scraping
2. Almacena estos precios en una base de datos
3. Calcula la equivalencia en dólares usando el tipo de cambio actual
4. Proporciona una API para que tu frontend pueda consumir estos datos

## Estructura del Proyecto Explicada

```
dolar-caro-backend/
├── models.py           # Define la estructura de los datos
├── db_manager.py       # Maneja la conexión con la base de datos
├── scrapers/           # Contiene el código para extraer precios de sitios web
│   ├── __init__.py     # Archivo necesario para que Python reconozca la carpeta como un módulo
│   ├── base_scraper.py # Código base para todos los scrapers
│   ├── nike_scraper.py # Código específico para extraer precios de Nike
│   └── adidas_scraper.py # Código específico para extraer precios de Adidas
├── services.py         # Coordina los scrapers y la base de datos
├── api.py              # Define los endpoints de la API que usará tu frontend
├── cli.py              # Herramienta para ejecutar comandos desde la terminal
├── utils.py            # Funciones de utilidad general
├── db/                 # Carpeta donde se guarda la base de datos SQLite
└── data/               # Carpeta donde se guardan los datos en formato JSON
```

## Explicación de Cada Archivo Principal

### 1. `models.py`
Define las "tablas" de la base de datos usando SQLAlchemy (un ORM - Object-Relational Mapper). Piensa en esto como la estructura de los datos:
- `Product`: Información de productos (Nike Air Force 1, camiseta de Argentina, etc.)
- `Country`: Países (Argentina, EE.UU.)
- `Price`: Precios de productos en diferentes países y fechas
- `Category`: Categorías de productos (calzado, ropa deportiva)

### 2. `db_manager.py`
Maneja todas las operaciones con la base de datos:
- Conectarse a la base de datos
- Guardar nuevos precios
- Obtener precios históricos
- Crear nuevos productos, países, etc.

### 3. Carpeta `scrapers/`
Contiene el código para extraer precios de sitios web:
- `base_scraper.py`: Código común para todos los scrapers (manejo de navegador, extracción de precios)
- `nike_scraper.py`: Código específico para extraer precios de Nike.com y Nike.com.ar
- `adidas_scraper.py`: Código específico para extraer precios de Adidas.com y Adidas.com.ar

### 4. `services.py`
Coordina todo el proceso:
- Inicia los scrapers para obtener precios
- Guarda los precios en la base de datos
- Calcula la equivalencia en dólares
- Formatea los datos para la API

### 5. `api.py`
Define los endpoints de la API que tu frontend puede consumir:
- `/nike`: Precios de Nike Air Force 1
- `/adidas`: Precios de la camiseta de Argentina
- `/all`: Todos los productos
- `/history/{endpoint}`: Datos históricos

### 6. `cli.py`
Una herramienta para ejecutar comandos desde la terminal:
- `python cli.py setup`: Configura la base de datos
- `python cli.py nike`: Obtiene precios de Nike
- `python cli.py adidas`: Obtiene precios de Adidas

### 7. `utils.py`
Funciones de utilidad general:
- Guardar datos históricos en archivos JSON
- Recuperar datos históricos

## Cómo Funciona Todo Junto

### 1. Configuración inicial
Se ejecuta `python cli.py setup` para crear la base de datos y añadir datos iniciales.

### 2. Obtención de precios
- Se ejecuta `python cli.py nike` o `python cli.py adidas`
- El sistema inicia un navegador invisible usando Playwright
- Navega a los sitios web de Nike/Adidas en Argentina y EE.UU.
- Extrae los precios (o usa valores predeterminados si falla)
- Guarda los precios en la base de datos y en archivos JSON

### 3. API para el frontend
- Se inicia el servidor con `python api.py` o `uvicorn api:app --reload`
- Tu frontend puede hacer peticiones a endpoints como:
  - `GET http://localhost:8000/nike`
  - `GET http://localhost:8000/adidas`
  - `GET http://localhost:8000/history/nike`

### 4. Formato de los datos
La API devuelve datos en formato JSON que incluyen:
- Nombre del producto
- Precio en Argentina (ARS)
- Precio en EE.UU. (USD)
- Precio de Argentina convertido a USD
- URLs de los productos
- Tipo de cambio utilizado

## Para Desarrolladores Frontend

Como desarrollador frontend, principalmente interactuarás con:

1. **La API**: Harás peticiones a los endpoints definidos en `api.py`
2. **El formato JSON**: Necesitarás entender la estructura de los datos devueltos
3. **Los comandos CLI**: Para actualizar manualmente los precios si es necesario

No necesitas preocuparte por los detalles internos de cómo funciona el scraping o la base de datos, solo necesitas saber cómo consumir la API y qué datos esperar.

## Ejemplo de Uso desde el Frontend

```javascript
// Ejemplo de cómo podrías consumir la API desde tu frontend
async function getNikePrices() {
  const response = await fetch('http://localhost:8000/nike');
  const data = await response.json();
  
  // Ahora puedes usar los datos
  console.log(`Nike Air Force 1 en Argentina: $${data.ar_price} ARS`);
  console.log(`Nike Air Force 1 en EE.UU.: $${data.us_price} USD`);
  console.log(`Equivalente en USD: $${data.ar_price_usd} USD`);
  
  // También puedes usar las URLs para enlaces
  // data.url_ar - URL del producto en Argentina
  // data.url_us - URL del producto en EE.UU.
}
```

## Conceptos de Python para Desarrolladores Frontend

Aquí hay algunos conceptos básicos de Python que te ayudarán a entender mejor el código:

### 1. Importaciones y Módulos
En Python, las importaciones funcionan de manera similar a los `import` o `require` en JavaScript:

```python
# Importar un módulo completo
import os

# Importar funciones específicas
from datetime import datetime

# Importar con alias
import pandas as pd
```

### 2. Clases y Objetos
Python es un lenguaje orientado a objetos, similar a las clases en JavaScript moderno:

```python
class Scraper:
    def __init__(self, url):
        self.url = url  # Similar a this.url = url en JS
    
    def scrape(self):
        # Método para extraer datos
        return {"precio": 100}
```

### 3. Funciones Asíncronas
Python tiene funciones asíncronas similares a las de JavaScript, pero con `async/await`:

```python
async def get_price():
    # Similar a async function en JS
    await asyncio.sleep(1)  # Similar a await new Promise(resolve => setTimeout(resolve, 1000))
    return 100
```

### 4. Gestores de Contexto (with)
Python usa `with` para manejar recursos automáticamente:

```python
with open("archivo.txt", "r") as f:
    contenido = f.read()
# El archivo se cierra automáticamente al salir del bloque
```

### 5. Tipado en Python
Python 3 permite tipado opcional, similar a TypeScript:

```python
def calcular_precio(cantidad: int, precio: float) -> float:
    return cantidad * precio
```

## Instalación y Ejecución

1. Clona el repositorio:

```bash
git clone https://github.com/franciscobeccaria/dolar-caro-be.git
cd dolar-caro-be
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Instala los navegadores para Playwright:

```bash
python -m playwright install chromium
```

4. Configura la base de datos:

```bash
python cli.py setup
```

5. Ejecuta los scrapers:

```bash
python cli.py nike
python cli.py adidas
```

6. Inicia el servidor API:

```bash
python api.py
```

La API estará disponible en `http://localhost:8000`
