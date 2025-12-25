# services/web_precios.py

import pandas as pd

def obtener_precios_web(producto):
    """
    Precios REFERENCIALES desde supermercados/mayoristas
    (estructura lista para scraping o API)
    """

    data = [
        {
            "proveedor": "Jumbo Rancagua",
            "ciudad": "Rancagua",
            "producto": producto,
            "precio": 1090,
            "fuente": "jumbo.cl"
        },
        {
            "proveedor": "Tottus San Francisco",
            "ciudad": "San Francisco",
            "producto": producto,
            "precio": 1050,
            "fuente": "tottus.cl"
        },
        {
            "proveedor": "Alvi Rancagua",
            "ciudad": "Rancagua",
            "producto": producto,
            "precio": 990,
            "fuente": "alvi.cl"
        }
    ]

    return pd.DataFrame(data)
