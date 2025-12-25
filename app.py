import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Importaciones de tus servicios locales
from services.precios import obtener_precios
from services.alertas import detectar_bajadas
from services.ranking import ranking_proveedores
from services.estadisticas import promedio_regional
from services.prediccion import predecir_precio
from services.web_precios import obtener_precios_web
from firebase_config import db

# 1. CONFIGURACIÓN DE PÁGINA (DEBE IR PRIMERO)
st.set_page_config(page_title="Mayorista6", layout="wide")

st.title("🏪 Mayorista6 – Cotizador Sexta Región")
st.success("🔥 Conectado a la base de datos de precios")

# ==============================
# ➕ INGRESO DE PRECIOS
# ==============================
st.subheader("➕ Agregar nuevo precio")

with st.form("nuevo_precio"):
    col1, col2 = st.columns(2)
    with col1:
        producto = st.text_input("Producto (ej: Arroz 1kg)")
        proveedor = st.text_input("Proveedor (ej: Mayorista Rancagua)")
    with col2:
        ciudad = st.selectbox("Ciudad", ["Rancagua", "Graneros", "San Francisco", "Machalí"])
        precio = st.number_input("Precio", min_value=0)
    
    fecha = st.date_input("Fecha", value=date.today())
    guardar = st.form_submit_button("Guardar en Base de Datos")

    if guardar and producto and proveedor:
        db.collection("precios").add({
            "producto": producto,
            "proveedor": proveedor,
            "ciudad": ciudad,
            "precio": precio,
            "fecha": fecha.isoformat()
        })
        st.success(f"✅ {producto} guardado correctamente")

st.divider()

# ==============================
# 📊 DATOS LOCALES Y ANÁLISIS
# ==============================
data = obtener_precios()
df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠ No hay datos en la base de datos. Agrega precios para activar el análisis.")
else:
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Alertas y Ranking
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🚨 Alertas de Bajada")
        alertas = detectar_bajadas(df)
        if not alertas.empty:
            st.dataframe(alertas[["producto", "proveedor", "precio", "precio_anterior"]], use_container_width=True)
        else:
            st.info("No se detectan bajas de precios hoy.")

    with col_b:
        st.subheader("🏆 Ranking de Ahorro")
        st.dataframe(ranking_proveedores(df), use_container_width=True)

    # Gráfico Regional
    st.subheader("📊 Precio Promedio por Ciudad")
    promedio = promedio_regional(df)
    fig = px.bar(promedio, x="ciudad", y="precio", color="producto", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    # Predicción
    st.subheader("🤖 Predicción IA (7 días)")
    prov_sel = st.selectbox("Selecciona un proveedor para proyectar:", df["proveedor"].unique())
    pred = predecir_precio(df, prov_sel)
    if pred:
        st.metric(label=f"Precio estimado en {prov_sel}", value=f"${pred}")
    else:
        st.warning("Se necesitan al menos 3 registros históricos de este proveedor para predecir.")

# ==============================
# 🌐 COMPARATIVA WEB (SUPERMERCADOS Y MAYORISTAS)
# ==============================
st.divider()
st.subheader("🌐 Comparador de Supermercados Online")
st.info("Busca precios en Jumbo, Lider, Tottus, Unimarc, Alvi y Casa García")

producto_web = st.text_input("Ingresa producto para comparar online (ej: Aceite):")

if producto_web:
    # Esta función ahora devuelve la lista extendida de supermercados
    df_web = obtener_precios_web(producto_web) 
    st.dataframe(df_web, use_container_width=True)

    fig_web = px.bar(
        df_web,
        x="proveedor",
        y="precio",
        color="proveedor",
        text_auto=True,
        title=f"Precios de '{producto_web}' en la red"
    )
    st.plotly_chart(fig_web, use_container_width=True)

# ==============================
# 💰 CALCULADORA DE VENTA
# ==============================
st.divider()
st.subheader("💰 Calculadora de Margen para tu Pyme")
c1, c2 = st.columns(2)
with c1:
    p_compra = st.number_input("Costo de compra ($)", min_value=0, value=1000)
with c2:
    p_margen = st.slider("Margen de ganancia %", 5, 100, 30)

v_venta = p_compra * (1 + p_margen / 100)
st.success(f"Sugerencia de venta: **${round(v_venta)}** | Ganancia: **${round(v_venta - p_compra)}** por unidad")