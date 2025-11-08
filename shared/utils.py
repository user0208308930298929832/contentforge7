
import os, json, random, base64, uuid
from datetime import date
from typing import Dict, Any, List, Tuple
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

DATA_DIR = "data"
USER_PATH = f"{DATA_DIR}/user.json"
POSTS_PATH = f"{DATA_DIR}/posts.json"
EVENTS_PATH = f"{DATA_DIR}/events.json"

DEFAULT_USER = {"brand":"Print Nest","niche":"moda sustentável","tone":"profissional","plan":"Starter","credits":120,"used":0,"images_today":0,"date":str(date.today())}

def ensure():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USER_PATH): json.dump(DEFAULT_USER, open(USER_PATH,"w"))
    if not os.path.exists(POSTS_PATH): json.dump([], open(POSTS_PATH,"w"))
    if not os.path.exists(EVENTS_PATH): json.dump([], open(EVENTS_PATH,"w"))

def load_user()->Dict[str,Any]: ensure(); return json.load(open(USER_PATH))
def save_user(u): json.dump(u, open(USER_PATH,"w"))
def load_posts()->List[Dict[str,Any]]: ensure(); return json.load(open(POSTS_PATH))
def save_posts(p): json.dump(p, open(POSTS_PATH,"w"))
def load_events()->List[Dict[str,Any]]: ensure(); return json.load(open(EVENTS_PATH))
def save_events(e): json.dump(e, open(EVENTS_PATH,"w"))

def roll_over_daily(u):
    today = str(date.today())
    if u.get("date") != today:
        u["images_today"] = 0; u["date"]=today; save_user(u)

def credits_left(u)->int: return max(0, u.get("credits",0)-u.get("used",0))
def consume_credits(u,n:int)->bool:
    if u.get("used",0)+n>u.get("credits",0): return False
    u["used"]=u.get("used",0)+n; save_user(u); return True

def get_openai():
    if OpenAI and os.getenv("OPENAI_API_KEY"): return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return None

def smart_hashtags(niche:str)->List[str]:
    cli=get_openai()
    base=["viral","foryou","dicas","pt","loja","moda","estilo","tendencia","sustentavel","look"]
    niche_tag = niche.replace(" ","").lower()[:16] or "marca"
    if not cli: return [niche_tag]+base[:9]
    try:
        res=cli.responses.create(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"), input=f"Gera 12 hashtags em pt-PT (sem #) para '{niche}'. Só vírgulas.", temperature=0.3)
        txt=res.output_text
        tags=[t.strip().strip('#') for t in txt.replace('\n',' ').split(',') if t.strip()]
        return ([niche_tag]+tags)[:12]
    except Exception:
        return [niche_tag]+base[:9]

def craft_caption(niche:str, tone:str, platform:str, instruction:str)->str:
    hook = f"{niche.title()}: menos ruído, mais propósito."
    body = f"No {platform}, usa gancho forte, prova social e CTA clara. {instruction or 'Hoje, mostra um exemplo prático.'}"
    cta = "Se ajudou, guarda e partilha."
    return f"{hook}\n\n{body}\n\n{cta}"

def score_post(caption:str, hashtags:str)->Tuple[int,int,int]:
    v=60+('?' in caption)*6+any(w in caption.lower() for w in ['guarda','comenta','partilha','escreve','clica'])*8
    v+= (len([x for x in hashtags.split('#') if x.strip()])>=5)*6
    v=max(55,min(97,v+random.randint(-4,8)))
    fit=max(55,min(95,60+random.randint(-4,6)))
    emo=max(55,min(95,58+random.randint(-5,10)))
    return int(v),int(fit),int(emo)

def smart_generate(niche:str, tone:str, platforms:List[str], total:int, instruction:str)->List[dict]:
    tags=smart_hashtags(niche); tag_str=" ".join(f"#{t}" for t in tags[:6])
    posts=[]
    for plat in platforms or ['instagram']:
        for _ in range(max(1,total//max(1,len(platforms)))):
            cap=craft_caption(niche,tone,plat,instruction)
            v,fit,emo=score_post(cap,tag_str)
            posts.append({"id":uuid.uuid4().hex[:8],"platform":plat,"title":f"{plat.title()} — Conteúdo","caption":cap,
                          "hashtags":tag_str,"virality":v,"fit":fit,"emotion":emo,"total":round((0.5*v+0.3*fit+0.2*emo),2)})
    posts.sort(key=lambda x: x["total"], reverse=True)
    if posts: posts[0]["recommended"]=True
    return posts

def generate_script(niche:str, instruction:str, platform:str='tiktok')->str:
    return f"""INTRO (0-3s): Gancho ligado a {niche} — {instruction or 'mostra o antes/depois em 3s'}.
PARTE 1 (3-8s): Problema comum do teu público.
PARTE 2 (8-18s): Tua solução em 3 passos (mostra bastidores).
PROVA (18-23s): Resultado em 1 frase.
FECHO (23-30s): CTA natural (ex: 'Comenta QUERO' para o guia)."""

def get_openai_image_b64(prompt:str, size='512x512'):
    cli=get_openai()
    if not cli: return None
    try:
        out=cli.images.generate(model="gpt-image-1", prompt=prompt, size=size, n=1)
        return out.data[0].b64_json
    except Exception:
        return None
