import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Inicialización segura para Streamlit Cloud
if not firebase_admin._apps:
    # Convertimos explícitamente a dict para evitar errores de formato de Streamlit
    firebase_key = dict(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()