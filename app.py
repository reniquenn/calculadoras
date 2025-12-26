import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Servicios
from services.precios import obtener_precios
from services.ocr_boleta import analizar_boleta
from services.prediccion import predecir_precio_avanzado
from firebase_config import db

st.set_page_config(page_title="Mayorista6 AI", layout="wide")
st.title("🏪 Mayorista6 – Inteligencia de Precios")

# ==============================
# 1. INGRESO DE DATOS (CON MARCA)
# ==============================
st.subheader("📝 Registrar Precios")
tab_manual, tab_scan = st.tabs(["Manual", "Escanear Boleta"])

with tab_manual:
    with st.form("form_manual"):
        c1, c2, c3 = st.columns(3)
        producto = c1.text_input("Producto", placeholder="Ej: Arroz")
        marca = c2.text_input("Marca", placeholder="Ej: Tucapel")
        proveedor = c3.text_input("Proveedor", placeholder="Ej: Lider")
        
        c4, c5 = st.columns(2)
        precio = c4.number_input("Precio", min_value=0)
        ciudad = c5.selectbox("Ciudad", ["Rancagua", "Machalí", "Graneros"])
        
        if st.form_submit_button("Guardar"):
            db.collection("precios").add({
                "producto": producto,
                "marca": marca, # NUEVO CAMPO
                "proveedor": proveedor,
                "precio": precio,
                "ciudad": ciudad,
                "fecha": date.today().isoformat()
            })
            st.success("Guardado!")

with tab_scan:
    img = st.file_uploader("Subir Boleta", type=["jpg", "png"])
    if img and st.button("Analizar con IA"):
        with st.spinner("Leyendo marcas y precios..."):
            df_ocr, fecha_ocr = analizar_boleta(img)
            if df_ocr is not None:
                # Editor permitiendo corregir MARCAS detectadas
                edited_df = st.data_editor(df_ocr, num_rows="dynamic", use_container_width=True)
                
                if st.button("Guardar Escaneo"):
                    batch = db.batch()
                    for _, row in edited_df.iterrows():
                        ref = db.collection("precios").document()
                        batch.set(ref, {
                            "producto": row["producto"],
                            "marca": row.get("marca", "Genérica"), # NUEVO
                            "proveedor": row["proveedor"],
                            "precio": int(row["precio"]),
                            "fecha": fecha_ocr,
                            "ciudad": "Rancagua"
                        })
                    batch.commit()
                    st.success("Boleta guardada con marcas detectadas.")

st.divider()

# ==============================
# 2. ANÁLISIS: LO MÁS BARATO
# ==============================
data = obtener_precios()
if data:
    df = pd.DataFrame(data)
    
    # Manejo de compatibilidad si datos viejos no tienen marca
    if "marca" not in df.columns:
        df["marca"] = "Desconocida"

    st.subheader("💰 El Buscador de Ahorro")
    
    col_search, col_result = st.columns([1, 2])
    
    with col_search:
        prod_sel = st.selectbox("¿Qué buscas?", df["producto"].unique())
        
    with col_result:
        # Lógica para encontrar lo MÁS BARATO de ese producto
        df_filtered = df[df["producto"] == prod_sel]
        min_row = df_filtered.loc[df_filtered["precio"].idxmin()]
        
        st.info(f"🥇 La opción más barata encontrada es:")
        st.metric(
            label=f"{min_row['marca']} en {min_row['proveedor']}",
            value=f"${min_row['precio']}",
            delta="Mejor precio"
        )
        
        st.markdown("#### Comparativa por Marca")
        # Gráfico que muestra variabilidad de precio por marca
        fig = px.box(df_filtered, x="marca", y="precio", color="proveedor", title=f"Dispersión de precios: {prod_sel}")
        st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # 3. PREDICCIÓN IA AVANZADA
    # ==============================
    st.divider()
    st.subheader("🤖 Predicción IA (Considera Marca)")
    
    c1, c2, c3 = st.columns(3)
    p_ia_prod = c1.selectbox("Producto IA", df["producto"].unique(), key="ia_p")
    
    # Filtro dinámico de marcas disponibles para ese producto
    marcas_avail = df[df["producto"] == p_ia_prod]["marca"].unique()
    p_ia_marca = c2.selectbox("Marca", marcas_avail)
    
    provs_avail = df[df["producto"] == p_ia_prod]["proveedor"].unique()
    p_ia_prov = c3.selectbox("Proveedor", provs_avail)
    
    if st.button("Predecir Precio Futuro"):
        # Llamamos a la nueva función
        precio_est = predecir_precio_avanzado(df[df["producto"] == p_ia_prod], p_ia_prov, p_ia_marca)
        st.success(f"Precio estimado para **{p_ia_prod} {p_ia_marca}** en {p_ia_prov}: **${precio_est}**")
        st.caption("Nota: La IA considera la inflación y el historial específico de esta marca.")

else:
    st.warning("Sube datos para comenzar.")