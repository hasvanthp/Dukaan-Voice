import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="DukaanAI", layout="wide")
st.title("DukaanAI — Voice-first Kirana Assistant")

st.write("Ask in Hinglish. Sensitive actions require confirmation.")

user_id = st.text_input("User ID (UUID)")
store_id = st.text_input("Store ID (UUID)")
text = st.text_area("Command", placeholder="Aaj kitni sales hui?")
confirmed = st.checkbox("Confirm sensitive action")

if st.button("Send"):
    if not user_id or not store_id or not text:
        st.error("User ID, Store ID and command are required")
    else:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/conversation/voice-command",
            json={"text": text, "confirmed": confirmed},
            headers={"x-user-id": user_id, "x-store-id": store_id},
            timeout=30,
        )
        st.json(response.json())
