
import streamlit as st, base64, uuid
from datetime import date
from shared.utils import load_user, save_user, credits_left, consume_credits, roll_over_daily, smart_generate, generate_script, get_openai_image_b64, load_posts, save_posts, load_events, save_events

st.set_page_config(page_title="ContentForge • Create", page_icon="✨", layout="wide")
st.markdown(open("assets/apple.css").read(), unsafe_allow_html=True)

u=load_user(); roll_over_daily(u)
st.title("Create ✨ • Smart Context Engine")
st.caption("Copy IA + hashtags + ⭐ recomendação • Roteiro IA (Pro+)")

with st.sidebar:
    st.write(f"**Marca:** {u['brand']}")
    st.write(f"**Nicho:** {u['niche']}")
    st.write(f"**Tom:** {u['tone']}")
    st.metric("Créditos", credits_left(u))
    st.caption(f"Plano: **{u['plan']}**")
    if st.button("Reset sessão"):
        save_posts([]); save_events([]); st.success("Sessão limpa.")

instruction = st.text_area("O que queres comunicar hoje? (Context Bar)", placeholder="Ex.: promoções, abertura de loja, história da marca…")
col1,col2,col3=st.columns([2,1,1])
platforms=col1.multiselect("Plataformas", ["instagram","tiktok"], default=["instagram","tiktok"])
total=col2.slider("Nº de ideias", 2, 12, 6)
want_image=col3.checkbox("Gerar thumbnail IA (512px)", value=(u["plan"]!="Starter"))

if st.button("⚡ Gerar agora"):
    need=max(1,total)
    if not consume_credits(u, need):
        st.warning("Créditos insuficientes.")
    else:
        posts=smart_generate(u["niche"], u["tone"], platforms, total, instruction)
        # imagens com limite por plano
        limits={"Starter":3,"Pro":6,"Prime":12}
        limit=limits.get(u["plan"],3)
        if want_image:
            for p in posts:
                if u["images_today"]<limit:
                    b64=get_openai_image_b64(f"{u['niche']} em fundo branco, estética Apple, sem texto.")
                    if b64: p["image_b64"]=b64; u["images_today"]+=1; save_user(u)
        allp=load_posts(); save_posts(posts+allp); st.success("Ideias criadas.")

posts=load_posts()
if not posts:
    st.info("Sem ideias ainda. Usa a barra de contexto e clica **Gerar agora**.")
else:
    st.markdown("### Ideias geradas")
    for p in posts[:20]:
        st.markdown('<div class="cf-card">', unsafe_allow_html=True)
        title=p["title"]
        if p.get("recommended"): title += "  <span class='cf-badge'>⭐ Nossa recomendação</span>"
        st.markdown(f"<div class='cf-title'>{title} <span class='cf-chip'>{p['platform']}</span></div>", unsafe_allow_html=True)
        st.write(p["caption"]); st.caption("Hashtags: "+p["hashtags"])
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Virality", f"{p['virality']}/100")
        c2.metric("Brand Fit", f"{p['fit']}")
        c3.metric("Emoção", f"{p['emotion']}")
        c4.metric("Score", f"{p['total']}")
        if u["plan"] in ["Pro","Prime"]:
            with st.expander("🎬 Roteiro IA (Pro+)"):
                st.text(generate_script(u["niche"], instruction, p["platform"]))
        # calendário
        dcol,tcol,addcol=st.columns([1,1,2])
        day=dcol.date_input("Dia", value=date.today(), key=f"d_{uuid.uuid4().hex}")
        tm=tcol.time_input("Hora", key=f"t_{uuid.uuid4().hex}")
        if addcol.button("📅 Adicionar ao calendário", key=f"add_{uuid.uuid4().hex}"):
            evs=load_events()
            evs.append({"title":p["title"],"start":f"{day.isoformat()}T{tm.isoformat()}",
                        "extendedProps":{"platform":p["platform"],"caption":p["caption"],"hashtags":p["hashtags"],
                                         "virality":p["virality"],"fit":p["fit"],"emotion":p["emotion"],"total":p["total"]}})
            save_events(evs); st.success("Adicionado ao calendário.")
        if p.get("image_b64"):
            st.image(base64.b64decode(p["image_b64"]), caption="Thumbnail IA (512px)", use_column_width=False)
        st.markdown('</div>', unsafe_allow_html=True)
