import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Importaciones de tus servicios locales
from services.precios import obtener_precios
from services.alertas import detectar_bajadas
from services.ranking import ranking_proveedores
from services.estadisticas import promedio_regional
# Importamos la nueva función de predicción IA
from services.prediccion import predecir_precio_ia
# Importamos ambas funciones de web
from services.web_precios import obtener_precios_web, obtener_tendencia_mercado
from firebase_config import db

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Mayorista6 AI", layout="wide")

st.title("🏪 Mayorista6 – Cotizador Inteligente con IA")

# ==============================
# ➕ INGRESO DE PRECIOS
# ==============================
with st.expander("➕ Agregar nuevo precio", expanded=False):
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
            try:
                db.collection("precios").add({
                    "producto": producto,
                    "proveedor": proveedor,
                    "ciudad": ciudad,
                    "precio": precio,
                    "fecha": fecha.isoformat()
                })
                st.success(f"✅ {producto} guardado correctamente")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

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

    # ==============================
    # 🤖 PREDICCIÓN IA AVANZADA
    # ==============================
    st.divider()
    st.subheader("🤖 Predicción de Precios con IA (Random Forest)")
    st.markdown("Este modelo cruza tus datos históricos con tendencias simuladas del mercado externo.")

    c_pred1, c_pred2 = st.columns(2)
    
    with c_pred1:
        # Selectores para filtrar qué predecir
        prod_lista = df["producto"].unique()
        prod_sel = st.selectbox("Selecciona Producto para IA:", prod_lista)
        
        # Filtramos proveedores que vendan ese producto
        prov_validos = df[df["producto"] == prod_sel]["proveedor"].unique()
        prov_sel = st.selectbox("Selecciona Proveedor:", prov_validos)

    with c_pred2:
        if st.button("🧠 Ejecutar Modelo Predictivo"):
            # 1. Obtenemos datos del mercado externo (Input para la IA)
            df_mercado = obtener_tendencia_mercado(prod_sel)
            
            # 2. Ejecutamos la predicción avanzada
            # Pasamos df filtrado por producto para que la IA se enfoque
            df_producto_interno = df[df["producto"] == prod_sel]
            
            precio_est, mensaje = predecir_precio_ia(df_producto_interno, prov_sel, df_mercado)
            
            if precio_est:
                st.metric(label=f"Precio Proyectado (7 días) - {prov_sel}", value=f"${precio_est}")
                st.caption(f"ℹ {mensaje}")
                
                # Gráfico explicativo
                # Unimos para graficar
                df_hist = df_producto_interno[df_producto_interno["proveedor"] == prov_sel].sort_values("fecha")
                fig_ia = px.line(df_hist, x="fecha", y="precio", title="Tu Histórico vs Predicción", markers=True)
                # Agregamos el punto de predicción
                fig_ia.add_scatter(
                    x=[pd.to_datetime(date.today() + pd.Timedelta(days=7))], 
                    y=[precio_est], 
                    mode='markers+text', 
                    name='Predicción IA',
                    text=[f"${precio_est}"],
                    marker=dict(size=15, color='red')
                )
                st.plotly_chart(fig_ia, use_container_width=True)
                
            else:
                st.warning(mensaje)

# ==============================
# 🌐 COMPARATIVA WEB
# ==============================
st.divider()
st.subheader("🌐 Comparador de Mercado en Tiempo Real")

producto_web = st.text_input("Buscar producto en la web (ej: Aceite):", value="Aceite")

if producto_web:
    df_web = obtener_precios_web(producto_web) 
    st.dataframe(df_web, use_container_width=True)

    fig_web = px.bar(
        df_web,
        x="proveedor",
        y="precio",
        color="proveedor",
        text_auto=True,
        title=f"Precios de '{producto_web}' hoy"
    )
    st.plotly_chart(fig_web, use_container_width=True)