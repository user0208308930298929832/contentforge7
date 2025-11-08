
import streamlit as st
from shared.utils import load_user, save_user, credits_left, roll_over_daily
st.set_page_config(page_title="ContentForge Hub", page_icon="🍏", layout="wide")
st.markdown(open("assets/apple.css").read(), unsafe_allow_html=True)

st.title("ContentForge • Hub 🍏")
st.caption("Perfil, plano e créditos.")

u=load_user(); roll_over_daily(u)
with st.sidebar:
    st.header("Perfil da Marca")
    u["brand"]=st.text_input("Nome da marca", u.get("brand",""))
    u["niche"]=st.text_input("Nicho/tema", u.get("niche",""))
    u["tone"]=st.selectbox("Tom", ["profissional","casual","emocional","premium"], index=0)
    st.metric("Créditos restantes", credits_left(u))
    st.caption(f"Plano: **{u.get('plan','Starter')}**")
    if st.button("Guardar"):
        save_user(u); st.success("Perfil guardado.")

st.markdown("""
**Apps disponíveis** (corre cada uma num terminal/instância):
- `create/app.py` — Geração IA + Roteiro (Pro+)
- `planner/app.py` — Calendário arrastável
- `performance/app.py` — Métricas gerais
""")
