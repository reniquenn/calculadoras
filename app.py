import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Importaciones de servicios
from services.precios import obtener_precios
from services.ocr_boleta import analizar_boleta
from services.prediccion import predecir_precio_avanzado
from firebase_config import db

st.set_page_config(page_title="Mayorista6 AI", layout="wide")
st.title("🏪 Mayorista6 – Inteligencia de Precios")

# ==============================
# 1. INGRESO DE DATOS (AHORA CON TAMAÑO/MEDIDA)
# ==============================
st.subheader("📝 Registrar Precios")
tab_manual, tab_scan = st.tabs(["Manual", "Escanear Boleta"])

with tab_manual:
    with st.form("form_manual"):
        st.markdown("##### Detalles del Producto")
        c1, c2, c3 = st.columns(3)
        producto = c1.text_input("Producto", placeholder="Ej: Bebida")
        marca = c2.text_input("Marca", placeholder="Ej: Coca Cola")
        # --- NUEVO CAMPO: Detalle para especificar tamaño ---
        detalle = c3.text_input("Medida/Tipo", placeholder="Ej: 3 Litros Retornable")
        
        st.markdown("##### Datos de Compra")
        c4, c5, c6 = st.columns(3)
        proveedor = c4.text_input("Proveedor", placeholder="Ej: Mayorista 10")
        precio = c5.number_input("Precio ($)", min_value=0, step=10)
        ciudad = c6.selectbox("Ciudad", ["Rancagua", "Machalí", "Graneros", "San Francisco"])
        
        if st.form_submit_button("Guardar"):
            if producto and precio > 0:
                # Construimos un nombre compuesto para facilitar búsquedas futuras
                nombre_full = f"{producto} {marca} {detalle}".strip()
                
                db.collection("precios").add({
                    "producto": producto,
                    "marca": marca if marca else "Genérica",
                    "detalle": detalle if detalle else "Estándar",
                    "nombre_completo": nombre_full, # Campo clave para el buscador
                    "proveedor": proveedor,
                    "precio": precio,
                    "ciudad": ciudad,
                    "fecha": date.today().isoformat()
                })
                st.success(f"✅ Guardado: {nombre_full} a ${precio}")
            else:
                st.warning("Debes ingresar al menos el nombre del producto y el precio.")

with tab_scan:
    # (Mantener tu lógica de OCR aquí, se actualizará sola al guardar en formato compatible)
    st.info("La función de escáner detectará automáticamente los productos.")
    img = st.file_uploader("Subir Boleta", type=["jpg", "png"])
    # ... (Aquí va tu código de OCR existente)

st.divider()

# ==============================
# 2. BUSCADOR INTELIGENTE (TIPO GOOGLE)
# ==============================
data = obtener_precios()
if data:
    df = pd.DataFrame(data)
    
    # Normalización de datos antiguos (por si faltan columnas nuevas)
    if "marca" not in df.columns: df["marca"] = ""
    if "detalle" not in df.columns: df["detalle"] = ""
    if "nombre_completo" not in df.columns: 
        df["nombre_completo"] = df["producto"] + " " + df["marca"] + " " + df["detalle"]

    st.subheader("💰 Buscador de Ahorro")
    
    # --- BARRA DE BÚSQUEDA TIPO GOOGLE ---
    col_search, col_stats = st.columns([2, 1])
    
    with col_search:
        query = st.text_input("🔍 ¿Qué buscas hoy?", placeholder="Ej: Bebida 3L, Arroz Tucapel, Harina...")
        
        if query:
            # FILTRO INTELIGENTE: Busca el texto en cualquiera de las columnas clave
            # Convierte todo a minúsculas para buscar sin importar mayúsculas
            mask = df.apply(lambda row: query.lower() in str(row["nombre_completo"]).lower() 
                                     or query.lower() in str(row["producto"]).lower()
                                     or query.lower() in str(row["marca"]).lower(), axis=1)
            df_results = df[mask].copy()
        else:
            df_results = df.copy() # Si no escriben nada, muestra todo (o podrías mostrar nada)

        # Mostrar Resultados Ordenados por Precio (De menor a mayor)
        if not df_results.empty:
            df_results = df_results.sort_values("precio", ascending=True)
            best_deal = df_results.iloc[0]
            
            st.success(f"🥇 Mejor opción: **{best_deal['producto']} {best_deal['marca']} {best_deal['detalle']}** a **${best_deal['precio']}** en **{best_deal['proveedor']}**")
            
            # Tabla interactiva con columnas ordenadas
            st.dataframe(
                df_results[["producto", "marca", "detalle", "precio", "proveedor", "fecha"]],
                column_config={
                    "precio": st.column_config.NumberColumn("Precio", format="$%d"),
                    "detalle": "Tamaño/Tipo"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No encontramos productos que coincidan con tu búsqueda.")

    with col_stats:
        if not df_results.empty and query:
            # Gráfico rápido de dispersión para ver dónde están los precios
            fig = px.strip(df_results, x="precio", y="proveedor", color="marca", 
                           title=f"Precios de '{query}'")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Escribe arriba para ver comparativas.")

else:
    st.warning("La base de datos está vacía. Agrega tu primer precio arriba.")