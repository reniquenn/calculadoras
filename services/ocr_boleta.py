import google.generativeai as genai
import PIL.Image
import json
import streamlit as st
import pandas as pd
from datetime import date

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass

def analizar_boleta(imagen_file):
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = PIL.Image.open(imagen_file)

    # Prompt actualizado para solicitar MARCA
    prompt = """
    Analiza esta boleta chilena. Extrae JSON con:
    1. "proveedor": Nombre del local.
    2. "fecha": YYYY-MM-DD.
    3. "items": Lista de objetos:
       - "producto": Tipo de producto genérico (ej: "Arroz", "Aceite", "Fideos"). NO incluyas la marca aquí.
       - "marca": La marca del producto (ej: "Tucapel", "Belmont", "Lucchetti"). Si no sale, usa "Genérica".
       - "precio": Precio unitario (entero).
       - "cantidad": Cantidad.
    """

    try:
        response = model.generate_content([prompt, img])
        texto_respuesta = response.text.replace("```json", "").replace("```", "").strip()
        datos = json.loads(texto_respuesta)
        
        if "items" in datos and datos["items"]:
            df = pd.DataFrame(datos["items"])
            df["proveedor"] = datos.get("proveedor", "Desconocido")
            df["ciudad"] = "Rancagua"
            return df, datos.get("fecha", date.today().isoformat())
        else:
            return None, None

    except Exception as e:
        st.error(f"Error IA: {e}")
        return None, None