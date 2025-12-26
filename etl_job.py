import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import random

# --- 1. Configuración de Acceso ---
try:
    # GitHub Actions creará este archivo temporalmente usando tu Secret
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error inicializando Firebase: {e}")
    pass

db = firestore.client()

# --- 2. Extracción de Precios (Simulada con Marcas) ---
def extraer_precios_mercado():
    productos_monitor = ["Aceite", "Arroz", "Azucar", "Harina", "Leche"]
    datos_extraidos = []

    for prod in productos_monitor:
        fuentes = [
            {"prov": "Lider", "marca": "Lider", "precio_base": 950},
            {"prov": "Casa Gamovi", "marca": "Tucapel", "precio_base": 1490}, # Sucursal Codegua/San Francisco
            {"prov": "Mayorista 10", "marca": "Acuenta", "precio_base": 890},
            {"prov": "Alvi", "marca": "Genérica", "precio_base": 870}
        ]

        for fuente in fuentes:
            precio_actual = fuente["precio_base"] + random.randint(-30, 30)
            datos_extraidos.append({
                "producto": prod,
                "marca": fuente["marca"],
                "proveedor": fuente["prov"],
                "precio": precio_actual,
                "fecha": datetime.now().isoformat(),
                "ciudad": "San Francisco" if fuente["prov"] == "Casa Gamovi" else "Rancagua",
                "origen": "ETL_AUTOMATICO"
            })
    return pd.DataFrame(datos_extraidos)

# --- 3. Carga a Firestore ---
def ejecutar_etl():
    print("Iniciando carga de precios de mercado...")
    df_nuevos = extraer_precios_mercado()
    batch = db.batch()
    # Usamos la misma colección para que la App pueda leer todo
    coleccion = db.collection("precios") 
    
    for _, row in df_nuevos.iterrows():
        doc_ref = coleccion.document()
        batch.set(doc_ref, row.to_dict())
        
    batch.commit()
    print(f"Éxito: Se cargaron {len(df_nuevos)} registros de referencia.")

if __name__ == "__main__":
    ejecutar_etl()