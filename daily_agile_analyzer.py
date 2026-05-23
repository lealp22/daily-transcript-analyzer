import os
from pathlib import Path

import requests
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PROMPT_PATH = APP_DIR / "prompt_daily_agile.txt"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"


def load_local_env() -> None:
    env_path = APP_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@st.cache_data(show_spinner=False)
def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def read_uploaded_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    raw_bytes = uploaded_file.getvalue()
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("utf-8", errors="replace")


def call_openrouter(api_key: str, model: str, prompt: str, transcript: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Daily Agile Analyzer",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    "Procesa la siguiente transcripcion de daily y devuelve "
                    "la salida en el formato solicitado:\n\n"
                    f"{transcript}"
                ),
            },
        ],
        "temperature": 0.4,
        "top_p": 0.8,
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


def main() -> None:
    load_local_env()

    st.set_page_config(
        page_title="Analizador de dailys agiles",
        page_icon="DA",
        layout="wide",
    )

    st.title("Analizador de dailys agiles")

    with st.sidebar:
        st.header("Configuracion")
        api_key = st.text_input(
            "OpenRouter API key",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password",
            help="Tambien puedes definir OPENROUTER_API_KEY en un fichero .env.",
        )
        model = st.text_input(
            "Modelo",
            value=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
            help="Ejemplo: openai/gpt-4o-mini, anthropic/claude-3.5-sonnet.",
        )

        with st.expander("Prompt cargado"):
            st.text_area(
                "Contenido de prompt_daily_agile.txt",
                value=load_prompt(),
                height=260,
                disabled=True,
            )

    uploaded_file = st.file_uploader(
        "Sube un documento de texto",
        type=["txt", "md", "csv", "log"],
    )
    uploaded_text = read_uploaded_text(uploaded_file)

    pasted_text = st.text_area(
        "O pega aqui la transcripcion",
        value=uploaded_text,
        height=300,
        placeholder="Pega aqui el texto de la daily...",
    )

    transcript = pasted_text.strip()
    can_process = bool(api_key.strip()) and bool(model.strip()) and bool(transcript)

    if st.button("Procesar transcripcion", type="primary", disabled=not can_process):
        with st.spinner("Procesando con OpenRouter..."):
            try:
                result = call_openrouter(
                    api_key=api_key.strip(),
                    model=model.strip(),
                    prompt=load_prompt(),
                    transcript=transcript,
                )
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "?"
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"OpenRouter devolvio un error HTTP {status}.")
                st.code(detail, language="json")
            except requests.RequestException as exc:
                st.error("No se pudo conectar con OpenRouter.")
                st.exception(exc)
            except (KeyError, IndexError) as exc:
                st.error("La respuesta de OpenRouter no tiene el formato esperado.")
                st.exception(exc)
            else:
                st.subheader("Resultado")
                st.markdown(result)
                st.download_button(
                    "Descargar resultado en Markdown",
                    data=result,
                    file_name="daily_analizada.md",
                    mime="text/markdown",
                )

    if not api_key.strip():
        st.info("Define tu API key de OpenRouter para habilitar el procesamiento.")
    elif not transcript:
        st.info("Sube un documento de texto o pega una transcripcion.")


if __name__ == "__main__":
    main()
