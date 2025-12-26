import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import timedelta

def predecir_precio_avanzado(df_historico, proveedor_objetivo, marca_objetivo, dias_futuro=7):
    """
    Modelo IA que considera: Historial + Marca + Proveedor + Factor Económico
    """
    # 1. Preparar datos
    df = df_historico.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    
    # 2. Ingeniería de Variables (Contexto Económico Simulado)
    # En un caso real, aquí harías scraping del valor del dólar u noticias
    # Si la fecha es reciente, asumimos un "factor inflacionario" más alto
    df["factor_economico"] = df["fecha"].apply(lambda x: 1.05 if x.year >= 2024 else 1.0)
    
    # Variables de tiempo
    df["dias_desde"] = (df["fecha"] - df["fecha"].min()).dt.days
    df["mes"] = df["fecha"].dt.month
    
    # 3. Codificación de Variables Categóricas (Marca y Proveedor)
    le_marca = LabelEncoder()
    le_prov = LabelEncoder()
    
    # Ajustamos encoders con todos los datos disponibles
    df["marca_code"] = le_marca.fit_transform(df["marca"].astype(str))
    df["prov_code"] = le_prov.fit_transform(df["proveedor"].astype(str))
    
    # 4. Entrenamiento
    features = ["dias_desde", "mes", "marca_code", "prov_code", "factor_economico"]
    X = df[features]
    y = df["precio"]
    
    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X, y)
    
    # 5. Predicción Futura
    # Necesitamos codificar los inputs del usuario
    try:
        marca_input = le_marca.transform([marca_objetivo])[0]
    except:
        # Si la marca es nueva, usamos la moda (la más común) o un promedio
        marca_input = df["marca_code"].mode()[0]

    try:
        prov_input = le_prov.transform([proveedor_objetivo])[0]
    except:
        prov_input = df["prov_code"].mode()[0]
        
    ultima_fecha = df["fecha"].max()
    fecha_pred = ultima_fecha + timedelta(days=dias_futuro)
    
    X_futuro = pd.DataFrame([{
        "dias_desde": (fecha_pred - df["fecha"].min()).days,
        "mes": fecha_pred.month,
        "marca_code": marca_input,
        "prov_code": prov_input,
        "factor_economico": 1.05 # Asumimos contexto actual
    }])
    
    prediccion = model.predict(X_futuro)[0]
    
    return int(prediccion)