import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    firebase_key = dict(st.secrets["FIREBASE_KEY"])

    # 🔴 FIX CRÍTICO: reparar saltos de línea
    firebase_key["private_key"] = firebase_key["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()
