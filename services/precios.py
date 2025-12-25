from firebase_config import db

def obtener_precios():
    docs = db.collection("precios").stream()
    return [doc.to_dict() for doc in docs]
