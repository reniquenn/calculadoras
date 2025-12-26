import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

def obtener_precios_web(producto):
    """
    Obtiene precios referenciales actuales (Snapshot del día).
    """
    data = [
        {"proveedor": "Jumbo Online", "ciudad": "Rancagua", "producto": producto, "precio": 1190, "fuente": "jumbo.cl"},
        {"proveedor": "Santa Isabel", "ciudad": "Rancagua", "producto": producto, "precio": 1150, "fuente": "santaisabel.cl"},
        {"proveedor": "Lider", "ciudad": "Graneros", "producto": producto, "precio": 1050, "fuente": "lider.cl"},
        {"proveedor": "Unimarc", "ciudad": "Rancagua", "producto": producto, "precio": 1220, "fuente": "unimarc.cl"},
        {"proveedor": "Mayorista 10", "ciudad": "San Francisco", "producto": producto, "precio": 990, "fuente": "m10.cl"},
        {"proveedor": "Alvi", "ciudad": "Rancagua", "producto": producto, "precio": 980, "fuente": "alvi.cl"}
    ]
    return pd.DataFrame(data)

def obtener_tendencia_mercado(producto):
    """
    Genera un histórico de precios promedio de mercado (competencia) para los últimos 60 días.
    Sirve para entrenar a la IA con variables externas.
    """
    fechas = [date.today() - timedelta(days=i) for i in range(60)]
    datos = []
    
    # Simulamos una tendencia de mercado con fluctuaciones (ruido)
    precio_base_mercado = 1100
    for f in fechas:
        # El precio varía ligeramente cada día (simulación de mercado)
        ruido = random.randint(-50, 50)
        # Tendencia al alza si es fin de mes (días > 25)
        factor_fecha = 1.05 if f.day > 25 else 1.0
        
        precio_dia = (precio_base_mercado + ruido) * factor_fecha
        
        datos.append({
            "fecha": pd.to_datetime(f),
            "precio_mercado_promedio": round(precio_dia)
        })
    
    return pd.DataFrame(datos)