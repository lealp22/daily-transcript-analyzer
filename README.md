# Analizador de dailys agiles

Aplicacion Streamlit para analizar transcripciones de reuniones daily de equipos de software. Permite subir un documento de texto o pegar una transcripcion, combina ese contenido con el prompt definido en `prompt_daily_agile.txt` y envia la peticion a un LLM usando OpenRouter.

El resultado se muestra en pantalla en formato Markdown y puede descargarse como fichero `.md`.

## Requisitos

- Python 3.10 o superior.
- `uv` instalado.
- Una API key de OpenRouter: https://openrouter.ai/

## Instalacion

Desde la carpeta del proyecto:

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

## Configuracion

La app necesita una API key de OpenRouter. Puedes introducirla directamente en la barra lateral de Streamlit o crear un fichero `.env` en la carpeta del proyecto:

```env
OPENROUTER_API_KEY=tu_api_key
OPENROUTER_MODEL=openrouter/free
```

`OPENROUTER_MODEL` es opcional. Si no se define, el script usa por defecto:

```text
openrouter/free
```

## Uso

Arranca la aplicacion con:

```powershell
streamlit run daily_agile_analyzer.py
```

Si estas usando el entorno virtual directamente:

```powershell
.venv\Scripts\python.exe -m streamlit run daily_agile_analyzer.py
```

Despues abre en el navegador:

```text
http://localhost:8501
```

En la interfaz:

1. Introduce tu API key de OpenRouter en la barra lateral, salvo que ya la tengas en `.env`.
2. Revisa o cambia el modelo si lo necesitas.
3. Sube un fichero de texto (`.txt`, `.md`, `.csv`, `.log`) o pega la transcripcion en el cuadro de texto.
4. Pulsa `Procesar transcripcion`.
5. Revisa el resultado y descargalo en Markdown si lo necesitas.

## Prompt

El prompt principal esta separado del codigo en:

```text
prompt_daily_agile.txt
```

Puedes modificar ese fichero para cambiar las instrucciones del analisis sin tocar el script Python.

## Ficheros principales

- `daily_agile_analyzer.py`: aplicacion Streamlit y llamada a OpenRouter.
- `prompt_daily_agile.txt`: prompt usado como instrucciones del sistema.
- `requirements.txt`: dependencias necesarias para ejecutar la app.
