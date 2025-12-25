from firebase_config import db

def obtener_productos():
    docs = db.collection("productos").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]
