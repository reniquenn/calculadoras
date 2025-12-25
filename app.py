import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from services.precios import obtener_precios
from services.alertas import detectar_bajadas
from services.ranking import ranking_proveedores
from services.estadisticas import promedio_regional
from services.prediccion import predecir_precio
from services.web_precios import obtener_precios_web
from firebase_config import db

st.set_page_config("Mayorista6", layout="wide")
st.title("🏪 Mayorista6 – Cotizador Sexta Región")

# ==============================
# ➕ INGRESO DE PRECIOS (SIEMPRE DISPONIBLE)
# ==============================
st.subheader("➕ Agregar nuevo precio")

with st.form("nuevo_precio"):
    producto = st.text_input("Producto (ej: Arroz 1kg)")
    proveedor = st.text_input("Proveedor (ej: Mayorista Rancagua)")
    ciudad = st.selectbox("Ciudad", ["Rancagua", "Graneros", "San Francisco", "Machalí"])
    precio = st.number_input("Precio", min_value=0)
    fecha = st.date_input("Fecha", value=date.today())

    guardar = st.form_submit_button("Guardar")

    if guardar and producto and proveedor:
        db.collection("precios").add({
            "producto": producto,
            "proveedor": proveedor,
            "ciudad": ciudad,
            "precio": precio,
            "fecha": fecha.isoformat()
        })
        st.success("✅ Precio guardado correctamente")

st.divider()

# ==============================
# 📊 DATOS LOCALES
# ==============================
data = obtener_precios()
df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠ No hay datos locales aún. Agrega precios para activar análisis.")
else:
    df["fecha"] = pd.to_datetime(df["fecha"])

    # ==============================
    # 🚨 ALERTAS
    # ==============================
    st.subheader("🚨 Alertas de Bajada de Precio")
    alertas = detectar_bajadas(df)

    if not alertas.empty:
        st.dataframe(alertas[["producto", "proveedor", "precio", "precio_anterior"]])
    else:
        st.success("Sin bajadas detectadas")

    # ==============================
    # 🏆 RANKING
    # ==============================
    st.subheader("🏆 Dónde conviene comprar hoy")
    st.dataframe(ranking_proveedores(df))

    # ==============================
    # 📊 PROMEDIO REGIONAL
    # ==============================
    st.subheader("📊 Precio Promedio Regional")
    promedio = promedio_regional(df)

    fig = px.bar(
        promedio,
        x="ciudad",
        y="precio",
        color="producto",
        title="Precio Promedio por Ciudad"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # 🤖 PREDICCIÓN
    # ==============================
    st.subheader("🤖 Predicción de Precios (7 días)")
    proveedor_sel = st.selectbox("Proveedor", df["proveedor"].unique())

    pred = predecir_precio(df, proveedor_sel)
    if pred:
        st.info(f"📈 Precio estimado en 7 días: ${pred}")
    else:
        st.warning("No hay datos suficientes para predecir")

# ==============================
# 🌐 PRECIOS DESDE WEBS
# ==============================
st.divider()
st.subheader("🌐 Precios referenciales desde supermercados")

producto_web = st.text_input("Producto a buscar en webs (ej: Arroz 1kg)")

if producto_web:
    df_web = obtener_precios_web(producto_web)
    st.dataframe(df_web)

    fig_web = px.bar(
        df_web,
        x="proveedor",
        y="precio",
        color="ciudad",
        title="Comparación precios web"
    )
    st.plotly_chart(fig_web, use_container_width=True)

# ==============================
# 💰 MARGEN
# ==============================
st.divider()
st.subheader("💰 Calculadora de Margen")

precio_base = st.number_input("Precio compra", 0)
margen = st.slider("Margen %", 5, 100, 30)

venta = precio_base * (1 + margen / 100)
ganancia = venta - precio_base

st.success(f"Precio sugerido venta: ${round(venta)}")
st.info(f"Ganancia por unidad: ${round(ganancia)}")
