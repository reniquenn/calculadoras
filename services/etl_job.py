import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import random

# --- 1. Configuración de Acceso (Simulada para local, usar Secrets en Prod) ---
# Si lo corres local, necesitas tu archivo firebase_key.json
try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
except:
    # Si ya está inicializado
    pass

db = firestore.client()

# --- 2. Servicio de Extracción Web (Simulado con Marcas) ---
def extraer_precios_web_actualizados():
    # Lista de productos que te interesa monitorear
    productos_monitor = ["Aceite", "Arroz", "Azucar", "Harina", "Leche"]
    datos_extraidos = []

    for prod in productos_monitor:
        # Simulamos scraping de diferentes sitios y MARCAS
        # En producción, aquí iría BeautifulSoup / Selenium
        fuentes = [
            {"prov": "Lider", "marca": "Lider", "precio_base": 900},
            {"prov": "Lider", "marca": "Tucapel", "precio_base": 1300},
            {"prov": "Jumbo", "marca": "Cuisine&Co", "precio_base": 1100},
            {"prov": "Jumbo", "marca": "Tucapel", "precio_base": 1450},
            {"prov": "Mayorista10", "marca": "Acuenta", "precio_base": 850}, # La opción barata
            {"prov": "Santa Isabel", "marca": "Monticello", "precio_base": 1250},
        ]

        for fuente in fuentes:
            # Variación diaria aleatoria
            precio_actual = fuente["precio_base"] + random.randint(-50, 50)
            
            datos_extraidos.append({
                "producto": prod,
                "marca": fuente["marca"],
                "proveedor": fuente["prov"],
                "precio": precio_actual,
                "fecha": datetime.now().isoformat(),
                "origen": "WEB_SCRAPER" # Etiqueta para saber que vino del ETL
            })
    
    return pd.DataFrame(datos_extraidos)

# --- 3. Carga (Load) a Firestore ---
def ejecutar_etl():
    print(f"[{datetime.now()}] Iniciando ETL de Precios...")
    
    df_nuevos = extraer_precios_web_actualizados()
    print(f" > Se encontraron {len(df_nuevos)} precios nuevos.")
    
    batch = db.batch()
    coleccion = db.collection("precios_mercado_web") # Colección separada para no ensuciar la tuya
    
    count = 0
    for _, row in df_nuevos.iterrows():
        doc_ref = coleccion.document() # ID automático
        batch.set(doc_ref, row.to_dict())
        count += 1
        
        # Firestore permite max 500 ops por batch
        if count >= 400:
            batch.commit()
            batch = db.batch()
            count = 0
            
    if count > 0:
        batch.commit()
        
    print(" > Carga completada exitosamente.")

if __name__ == "__main__":
    ejecutar_etl()