def ranking_proveedores(df):
    hoy = df["fecha"].max()
    df_hoy = df[df["fecha"] == hoy]

    ranking = (
        df_hoy.groupby("proveedor")["precio"]
        .mean()
        .sort_values()
        .reset_index()
    )

    return ranking
