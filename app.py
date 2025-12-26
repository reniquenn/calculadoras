import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Importaciones de tus servicios locales
from services.precios import obtener_precios
from services.alertas import detectar_bajadas
from services.ranking import ranking_proveedores
from services.estadisticas import promedio_regional
# Servicios de IA (Predicción y OCR)
from services.prediccion import predecir_precio_ia
from services.ocr_boleta import analizar_boleta
# Servicios Web
from services.web_precios import obtener_precios_web, obtener_tendencia_mercado
from firebase_config import db

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Mayorista6 AI", layout="wide")

st.title("🏪 Mayorista6 – Cotizador Inteligente con IA")
st.markdown("Gestión de precios, escaneo de boletas y predicciones de mercado.")

# ==============================
# ➕ INGRESO DE PRECIOS (MANUAL O IA)
# ==============================
st.divider()
st.subheader("➕ Agregar Precios")

tab_manual, tab_scan = st.tabs(["📝 Ingreso Manual", "📸 Escanear Boleta (IA)"])

# --- PESTAÑA 1: INGRESO MANUAL ---
with tab_manual:
    with st.form("nuevo_precio"):
        col1, col2 = st.columns(2)
        with col1:
            producto = st.text_input("Producto (ej: Arroz 1kg)")
            proveedor = st.text_input("Proveedor (ej: Mayorista Rancagua)")
        with col2:
            ciudad = st.selectbox("Ciudad", ["Rancagua", "Graneros", "San Francisco", "Machalí"])
            precio = st.number_input("Precio", min_value=0)
        
        fecha = st.date_input("Fecha", value=date.today())
        guardar = st.form_submit_button("Guardar Manual")

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

# --- PESTAÑA 2: ESCANEAR BOLETA (IA) ---
with tab_scan:
    st.info("Sube una foto de tu boleta o usa la cámara. La IA detectará los productos automáticamente.")
    
    opcion_input = st.radio("Seleccionar método:", ["Subir Archivo", "Usar Cámara"], horizontal=True)
    
    imagen_input = None
    if opcion_input == "Subir Archivo":
        imagen_input = st.file_uploader("Sube la foto de la boleta", type=["jpg", "png", "jpeg"])
    else:
        imagen_input = st.camera_input("Toma una foto de la boleta")

    if imagen_input:
        if st.button("🤖 Procesar Boleta con IA"):
            with st.spinner("Analizando imagen con Gemini Flash..."):
                df_detectado, fecha_detectada = analizar_boleta(imagen_input)
            
            if df_detectado is not None:
                st.success(f"✅ Productos detectados con fecha {fecha_detectada}. Revisa la tabla y edita si es necesario.")
                
                # Editor de datos permite corregir si la IA se equivocó
                df_editor = st.data_editor(
                    df_detectado, 
                    num_rows="dynamic", 
                    use_container_width=True,
                    column_config={
                        "precio": st.column_config.NumberColumn("Precio", format="$%d"),
                        "cantidad": st.column_config.NumberColumn("Cant.", format="%d")
                    }
                )
                
                if st.button("💾 Guardar Todo en Base de Datos"):
                    count = 0
                    batch = db.batch() # Usamos batch para guardar todo junto
                    
                    for index, row in df_editor.iterrows():
                        doc_ref = db.collection("precios").document()
                        batch.set(doc_ref, {
                            "producto": row["producto"],
                            "proveedor": row["proveedor"],
                            "ciudad": row["ciudad"],
                            "precio": int(row["precio"]),
                            "fecha": fecha_detectada
                        })
                        count += 1
                    
                    try:
                        batch.commit()
                        st.balloons()
                        st.success(f"¡Se guardaron {count} productos exitosamente!")
                    except Exception as e:
                        st.error(f"Error al guardar batch: {e}")
            else:
                st.warning("No se pudieron detectar productos o la imagen no es clara.")

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
    st.subheader("🤖 Predicción de Precios con IA")
    st.markdown("Modelo Random Forest: Cruza historial interno + tendencias de mercado externo.")

    c_pred1, c_pred2 = st.columns(2)
    
    with c_pred1:
        # Selectores
        prod_lista = df["producto"].unique()
        prod_sel = st.selectbox("Selecciona Producto para IA:", prod_lista)
        
        # Filtramos proveedores
        prov_validos = df[df["producto"] == prod_sel]["proveedor"].unique()
        prov_sel = st.selectbox("Selecciona Proveedor:", prov_validos)

    with c_pred2:
        if st.button("🧠 Ejecutar Predicción"):
            # 1. Obtenemos datos del mercado externo (simulado para entrenamiento)
            df_mercado = obtener_tendencia_mercado(prod_sel)
            
            # 2. Ejecutamos la predicción avanzada
            df_producto_interno = df[df["producto"] == prod_sel]
            
            precio_est, mensaje = predecir_precio_ia(df_producto_interno, prov_sel, df_mercado)
            
            if precio_est:
                st.metric(label=f"Precio Proyectado (7 días) - {prov_sel}", value=f"${precio_est}")
                st.caption(f"ℹ {mensaje}")
                
                # Gráfico explicativo
                df_hist = df_producto_interno[df_producto_interno["proveedor"] == prov_sel].sort_values("fecha")
                fig_ia = px.line(df_hist, x="fecha", y="precio", title="Histórico vs Predicción IA", markers=True)
                
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
st.info("Busca precios referenciales en supermercados online.")

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

# ==============================
# 💰 CALCULADORA
# ==============================
st.divider()
st.subheader("💰 Calculadora de Margen Pyme")
c1, c2 = st.columns(2)
with c1:
    p_compra = st.number_input("Costo de compra ($)", min_value=0, value=1000)
with c2:
    p_margen = st.slider("Margen de ganancia %", 5, 100, 30)

v_venta = p_compra * (1 + p_margen / 100)
st.success(f"Sugerencia de venta: **${round(v_venta)}** | Ganancia: **${round(v_venta - p_compra)}**")