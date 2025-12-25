import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Inicialización segura para Streamlit Cloud
if not firebase_admin._apps:
    firebase_key = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()
