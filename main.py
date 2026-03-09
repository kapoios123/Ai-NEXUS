import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from litellm import completion
import json
import os
import requests

st.set_page_config(page_title="AI Nexus", page_icon="🤖", layout="wide")

# 1. INITIALIZATIONS
if "user_email" not in st.session_state: st.session_state.user_email = None
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "chat" not in st.session_state: st.session_state.chat = []
if "db" not in st.session_state: st.session_state.db = None
if "context_memory" not in st.session_state: st.session_state.context_memory = ""

# 2. SIDEBAR
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Firebase Web API Key", type="password")
    firebase_file = st.file_uploader("Upload serviceAccountKey.json", type=["json"])
    
    if firebase_file and not firebase_admin._apps:
        try:
            key_data = json.load(firebase_file)
            cred = credentials.Certificate(key_data)
            firebase_admin.initialize_app(cred)
            st.session_state.db = firestore.client()
            st.success("Firebase Connected!")
        except Exception as e: st.error(e)

    if st.session_state.logged_in:
        st.divider()
        st.subheader("Cloud Settings")
        
        # Φόρτωση μοντέλων
        if "loaded_models" not in st.session_state:
            st.session_state.loaded_models = "gemini/gemini-1.5-flash-latest\ngroq/llama-3.3-70b-versatile\nmistral/mistral-large-latest"
            if st.session_state.db:
                user_doc = st.session_state.db.collection("users").document(st.session_state.user_email).get()
                if user_doc.exists and "models_list" in user_doc.to_dict():
                    st.session_state.loaded_models = user_doc.to_dict()["models_list"]
        
        models_input = st.text_area("Models", value=st.session_state.loaded_models, key="model_area")
        st.session_state.loaded_models = models_input
        
        model_list = [m.strip() for m in models_input.split("\n") if m.strip()]
        selected_model = st.selectbox("Select Model", model_list)
        
        # Ασφαλής ορισμός provider
        provider = selected_model.split('/')[0].upper() if '/' in selected_model else "AI"
        key_input = st.text_input(f"API Key for {provider}", type="password", key=f"key_{provider}")
        
        if st.button("Save Settings"):
            if st.session_state.db:
                st.session_state.db.collection("users").document(st.session_state.user_email).set({
                    "api_keys": {provider: key_input},
                    "selected_model": selected_model,
                    "models_list": models_input
                }, merge=True)
                os.environ[f"{provider}_API_KEY"] = key_input
                st.success("Settings Saved!")

        st.divider()
        # ΕΠΑΝΑΦΟΡΑ ΤΟΥ SYNC HISTORY (Εδώ το χάσαμε πριν!)
        if st.button("🔄 Sync History (Silent)"):
            if st.session_state.db and st.session_state.user_email:
                docs = st.session_state.db.collection("users").document(st.session_state.user_email)\
                        .collection("chats").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(15).stream()
                
                history_list = []
                for d in reversed(list(docs)):
                    data = d.to_dict()
                    history_list.append(f"User: {data['prompt']}\nAI: {data['response']}")
                
                st.session_state.context_memory = "\n\n".join(history_list)
                st.sidebar.success("History synced to AI memory!")

# 3. AUTH LOGIC
def firebase_auth(email, password, api_key, mode="login"):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{'signInWithPassword' if mode=='login' else 'signUp'}?key={api_key}"
    try:
        r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
        if r.status_code == 200:
            st.session_state.user_email = email
            return True, None
        return False, r.json().get("error", {}).get("message", "Login Failed")
    except Exception as e: return False, str(e)

if not st.session_state.logged_in:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not api_key: st.error("Enter Firebase Key")
        elif not st.session_state.db: st.error("Please upload serviceAccountKey.json first!")
        else:
            success, msg = firebase_auth(email, password, api_key)
            if success:
                st.session_state.logged_in = True
                user_doc = st.session_state.db.collection("users").document(email).get()
                if user_doc.exists:
                    data = user_doc.to_dict()
                    if "api_keys" in data:
                        for p, k in data["api_keys"].items(): os.environ[f"{p}_API_KEY"] = k
                st.rerun()
            else: st.error(msg)
    st.stop()

# 4. CHAT UI
st.title(f"🤖 AI Nexus - User: {st.session_state.user_email}")
for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Ask something"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        try:
            full_prompt = f"Previous Context:\n{st.session_state.context_memory}\n\nUser Question: {prompt}"
            response = completion(model=selected_model, messages=[{"role": "user", "content": full_prompt}])
            reply = response.choices[0].message.content
            st.write(reply)
            
            if st.session_state.db:
                st.session_state.db.collection("users").document(st.session_state.user_email).collection("chats").add({
                    "prompt": prompt, "response": reply, "timestamp": firestore.SERVER_TIMESTAMP
                })
        except Exception as e: 
            reply = f"AI Error: {str(e)}"
            st.error(reply)
    
    st.session_state.chat.append({"role": "assistant", "content": reply})