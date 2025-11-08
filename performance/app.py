
import streamlit as st, statistics as stats
from shared.utils import load_posts, load_events
st.set_page_config(page_title="ContentForge • Performance", page_icon="📊", layout="wide")
st.markdown(open("assets/apple.css").read(), unsafe_allow_html=True)

st.title("Performance 📊 • Visão Geral")
st.caption("Métricas simuladas com base nos conteúdos gerados (reais em planos superiores).")

posts=load_posts(); evs=load_events()
if not posts:
    st.info("Gera conteúdo no módulo Create para veres as métricas.")
else:
    vir=[p.get('virality',0) for p in posts]
    fit=[p.get('fit',0) for p in posts]
    emo=[p.get('emotion',0) for p in posts]
    st.markdown('<div class="cf-card">', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Virality médio", f"{int(stats.mean(vir))}/100")
    c2.metric("Brand Fit médio", f"{int(stats.mean(fit))}")
    c3.metric("Emoção média", f"{int(stats.mean(emo))}")
    c4.metric("Posts gerados", len(posts))
    st.markdown('</div>', unsafe_allow_html=True)

if evs:
    st.markdown('<div class="cf-card">', unsafe_allow_html=True)
    st.subheader("Resumo do calendário")
    st.write(f"Eventos agendados: **{len(evs)}**")
    st.caption("Edita e organiza no módulo Planner.")
    st.markdown('</div>', unsafe_allow_html=True)
