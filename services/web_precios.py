import pandas as pd

def obtener_precios_web(producto):
    """
    Obtiene precios referenciales de cadenas con presencia en la Sexta Región.
    Nota: En una fase avanzada, aquí se integraría el scraping real.
    """
    # Lista de proveedores solicitados
    data = [
        {"proveedor": "Jumbo", "ciudad": "Rancagua", "producto": producto, "precio": 1090, "fuente": "jumbo.cl"},
        {"proveedor": "Tottus", "ciudad": "San Francisco", "producto": producto, "precio": 1050, "fuente": "tottus.cl"},
        {"proveedor": "Alvi (Mayorista)", "ciudad": "Rancagua", "producto": producto, "precio": 990, "fuente": "alvi.cl"},
        {"proveedor": "Lider", "ciudad": "Graneros", "producto": producto, "precio": 1020, "fuente": "lider.cl"},
        {"proveedor": "Unimarc", "ciudad": "Rancagua", "producto": producto, "precio": 1150, "fuente": "unimarc.cl"},
        {"proveedor": "Casa García", "ciudad": "Rancagua", "producto": producto, "precio": 980, "fuente": "casagarcia.cl"},
        {"proveedor": "Mayorista 10", "ciudad": "San Francisco", "producto": producto, "precio": 1000, "fuente": "m10.cl"}
    ]
    
    df_web = pd.DataFrame(data)
    return df_web