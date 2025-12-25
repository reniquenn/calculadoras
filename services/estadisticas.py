def promedio_regional(df):
    return (
        df.groupby(["producto", "ciudad"])["precio"]
        .mean()
        .reset_index()
    )
