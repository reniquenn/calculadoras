import google.generativeai as genai
import PIL.Image
import json
import streamlit as st
import pandas as pd
from datetime import date

# Configuración de la API (La clave debe estar en secrets)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass # Se manejará el error en la UI si falta la key

def analizar_boleta(imagen_file):
    """
    Toma una imagen (bytes o file-like), la envía a Gemini Flash
    y retorna un DataFrame con los productos detectados.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    img = PIL.Image.open(imagen_file)

    prompt = """
    Analiza esta imagen de una boleta o factura de compra chilena.
    Extrae la siguiente información y entrégala estrictamente en formato JSON:
    1. "proveedor": Nombre del supermercado o negocio.
    2. "fecha": Fecha de compra en formato YYYY-MM-DD (si no es visible, usa la fecha de hoy).
    3. "items": Una lista de objetos, donde cada uno tiene:
       - "producto": Nombre descriptivo del producto.
       - "precio": El precio unitario (entero, sin símbolos).
       - "cantidad": La cantidad comprada (si aplica, sino 1).
    
    Si hay descuentos, usa el precio final pagado.
    Responde SOLO con el JSON, sin texto adicional ni bloques de código markdown.
    """

    try:
        response = model.generate_content([prompt, img])
        texto_respuesta = response.text.replace("```json", "").replace("```", "").strip()
        
        datos = json.loads(texto_respuesta)
        
        # Convertimos la lista de items a DataFrame para facilitar la edición
        if "items" in datos and datos["items"]:
            df = pd.DataFrame(datos["items"])
            # Agregamos proveedor y fecha a cada fila para que el usuario no tenga que repetirlo
            df["proveedor"] = datos.get("proveedor", "Desconocido")
            # Agregamos columna ciudad por defecto (usuario debe confirmar)
            df["ciudad"] = "Rancagua" 
            return df, datos.get("fecha", date.today().isoformat())
        else:
            return None, None

    except Exception as e:
        st.error(f"Error al procesar la boleta: {e}")
        return None, None