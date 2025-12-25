import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def predecir_precio(df, proveedor):
    df_p = df[df["proveedor"] == proveedor].copy()

    if len(df_p) < 3:
        return None

    df_p["fecha"] = pd.to_datetime(df_p["fecha"])
    df_p["dias"] = (df_p["fecha"] - df_p["fecha"].min()).dt.days

    X = df_p[["dias"]]
    y = df_p["precio"]

    model = LinearRegression()
    model.fit(X, y)

    futuro = np.array([[df_p["dias"].max() + 7]])
    prediccion = model.predict(futuro)[0]

    return round(prediccion, 0)
