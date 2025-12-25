import pandas as pd

def detectar_bajadas(df):
    df = df.sort_values(["proveedor", "fecha"])
    df["precio_anterior"] = df.groupby("proveedor")["precio"].shift(1)
    df["bajo"] = df["precio"] < df["precio_anterior"]

    alertas = df[df["bajo"]]
    return alertas
