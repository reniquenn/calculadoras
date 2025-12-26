import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta

def predecir_precio_ia(df_interno, proveedor, df_mercado):
    """
    Predice el precio usando un modelo Random Forest que cruza datos internos 
    con tendencias de mercado externas.
    """
    # 1. Filtrar datos del proveedor seleccionado
    df_p = df_interno[df_interno["proveedor"] == proveedor].copy()
    
    if len(df_p) < 5:
        return None, "Insuficientes datos para IA (mínimo 5 registros)"

    # 2. Preparación de datos (Feature Engineering)
    df_p["fecha"] = pd.to_datetime(df_p["fecha"])
    df_mercado["fecha"] = pd.to_datetime(df_mercado["fecha"])
    
    # Unir tus precios con los del mercado por fecha (aprox)
    df_full = pd.merge_asof(
        df_p.sort_values("fecha"), 
        df_mercado.sort_values("fecha"), 
        on="fecha", 
        direction="nearest"
    )

    # Crear variables predictoras (Features)
    df_full["dias_desde_inicio"] = (df_full["fecha"] - df_full["fecha"].min()).dt.days
    df_full["dia_mes"] = df_full["fecha"].dt.day
    df_full["dia_semana"] = df_full["fecha"].dt.dayofweek
    df_full["es_fin_mes"] = df_full["dia_mes"] > 25  # Variable binaria

    # Definir X (Entradas) e y (Salida)
    # La IA aprende: [Días pasados, Precio Competencia, Día del mes] -> [Tu Precio]
    features = ["dias_desde_inicio", "precio_mercado_promedio", "dia_mes", "dia_semana"]
    
    # Manejo de datos vacíos si el merge falló en algún punto
    df_full = df_full.dropna(subset=features + ["precio"])

    X = df_full[features]
    y = df_full["precio"]

    # 3. Entrenamiento del Modelo (Random Forest)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 4. Predicción a futuro (7 días)
    ultima_fecha = df_full["fecha"].max()
    fecha_futura = ultima_fecha + timedelta(days=7)
    
    # Para predecir, necesitamos asumir el precio del mercado en 7 días.
    # Usamos el último precio de mercado conocido como base.
    ultimo_precio_mercado = df_full["precio_mercado_promedio"].iloc[-1]
    
    datos_futuros = pd.DataFrame([{
        "dias_desde_inicio": (fecha_futura - df_full["fecha"].min()).days,
        "precio_mercado_promedio": ultimo_precio_mercado, # Asumimos estabilidad mercado
        "dia_mes": fecha_futura.day,
        "dia_semana": fecha_futura.dayofweek
    }])

    prediccion = model.predict(datos_futuros)[0]
    
    return round(prediccion), f"Basado en {len(df_full)} registros y tendencias de mercado"