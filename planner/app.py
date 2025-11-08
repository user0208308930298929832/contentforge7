
import streamlit as st, pandas as pd
from shared.utils import load_events, save_events
st.set_page_config(page_title="ContentForge • Planner", page_icon="📅", layout="wide")
st.markdown(open("assets/apple.css").read(), unsafe_allow_html=True)

st.title("Planner 📅 • Calendário & Planeamento")
st.caption("Arrasta e organiza. Clica para detalhes.")

USE_CAL=True
try:
    from streamlit_calendar import calendar
except Exception:
    USE_CAL=False

events=[e for e in load_events() if isinstance(e,dict) and "title" in e and "start" in e]

if USE_CAL:
    options={"initialView":"timeGridWeek","slotMinTime":"08:00:00","slotMaxTime":"22:00:00","themeSystem":"standard","dayMaxEvents":True}
    cal=calendar(events=events, options=options, key="cal1")
    if isinstance(cal,dict) and cal.get("eventsSet"):
        save_events(cal["eventsSet"])
else:
    st.warning("Componente de calendário indisponível. A mostrar lista.")
    st.dataframe(pd.DataFrame(events), use_container_width=True)

st.markdown("---")
st.subheader("Detalhes")
events=[e for e in load_events() if isinstance(e,dict) and "title" in e]
if events:
    titles=["—"]+[e["title"] for e in events]
    sel=st.selectbox("Escolhe um evento", options=titles)
    if sel!="—":
        e=next(x for x in events if x["title"]==sel)
        ep=e.get("extendedProps",{})
        st.markdown('<div class="cf-card">', unsafe_allow_html=True)
        st.write(f"**Quando:** {e.get('start','-')}  |  **Plataforma:** {ep.get('platform','-')}")
        st.write("**Legenda**"); st.write(ep.get("caption",""))
        st.caption("Hashtags: "+ep.get("hashtags",""))
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Virality", f"{ep.get('virality',0)}/100")
        c2.metric("Brand Fit", f"{ep.get('fit',0)}")
        c3.metric("Emoção", f"{ep.get('emotion',0)}")
        c4.metric("Score", f"{ep.get('total',0)}")
        if st.button("Remover do calendário"):
            save_events([x for x in events if x["title"]!=sel]); st.success("Removido.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Sem eventos. Adiciona a partir do módulo Create.")

st.markdown("---")
st.subheader("Planeamento IA — adicionar sugestões")
if st.button("📌 Preencher semana com IA"):
    import datetime as dt
    evs=load_events()
    today=dt.date.today()
    start=today + dt.timedelta(days=(7 - today.weekday()) % 7)
    for i in range(5):
        day=start+dt.timedelta(days=i)
        evs.append({"title":"Sugestão IA — Publicação 19h","start":f"{day.isoformat()}T19:00:00",
                    "extendedProps":{"platform":"instagram","caption":"(slot sugerido)","hashtags":"",
                                     "virality":70,"fit":70,"emotion":70,"total":70}})
    save_events(evs); st.success("Semana sugerida adicionada.")
