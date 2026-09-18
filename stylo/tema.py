"""
Tema visual do Portal Alto Valor — Alloha Fibra / Giga+ Fibra.

Conceito: "luz na fibra". A base é o azul-noite da marca Alloha; o verde
Alloha é a luz que corre pela fibra (ações, confirmações, destaques) e o
ciano Giga+ é o segundo feixe (informação, links). O corpo do app é claro
porque é usado em campo, no celular, sob sol — legibilidade primeiro.
A única cena "cinematográfica" é o hero de fibra (Three.js + GSAP) no login
e no início; nas demais telas o movimento se limita a uma entrada
orquestrada quando a página abre.
"""
from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

RAIZ = Path(__file__).resolve().parent.parent
LOGO_POSITIVO = str(RAIZ / "assets" / "logo_alloha.png")
LOGO_NEGATIVO = str(RAIZ / "assets" / "logo_alloha_negativo.png")

CORES = {
    "noite": "#001059",      # azul Alloha (logo)
    "noite_2": "#0B1D78",
    "abismo": "#000A3B",
    "verde": "#44EE67",      # verde Alloha (logo)
    "verde_tinta": "#0E8A34",  # verde legível sobre fundo claro
    "ciano": "#00A7E1",      # feixe Giga+
    "papel": "#F4F6FB",
    "tinta": "#0B1542",
    "nevoa": "#5A6391",
    "linha": "#D6DCEB",
}

def _iframe(html: str, altura: int):
    """st.iframe (Streamlit >= 1.5x) com fallback para components.html."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=max(altura, 1))
    else:
        components.html(html, height=altura)


GSAP_CDN = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"
THREE_CDN = "https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"


# ─────────────────────────────────────────────────────────────────────────────
# CSS global
# ─────────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap');

:root{
  --noite:#001059; --noite-2:#0B1D78; --abismo:#000A3B;
  --verde:#44EE67; --verde-tinta:#0E8A34; --ciano:#00A7E1;
  --papel:#050608; --cartao:#0E1120; --cartao-2:#141830; --tinta:#EEF1FF; --nevoa:#98A1CF; --linha:#222846;
  --raio-g:18px; --raio-m:12px; --raio-p:8px;
  --sombra: 0 1px 0 rgba(255,255,255,.03) inset, 0 16px 36px -22px rgba(0,0,0,.9);
}

html, body, .stApp, [class*="st-"], button, input, textarea, select{
  font-family:'Lexend', system-ui, sans-serif !important;
  font-feature-settings:"tnum" 1;
}
/* ícones do Streamlit usam fonte própria (ligaduras): não sobrescrever */
[data-testid="stIconMaterial"], span[translate="no"], .material-symbols-rounded{
  font-family:'Material Symbols Rounded' !important; font-feature-settings:"liga" 1 !important;
}
.stApp{ background:var(--papel); color:var(--tinta); }

/* chrome do Streamlit */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"]{ display:none !important; }
/* botão de abrir/fechar a sidebar sempre visível */
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarCollapseButton"]{
  display:flex !important; visibility:visible !important; }
[data-testid="stExpandSidebarButton"] svg, [data-testid="stSidebarCollapsedControl"] svg{ color:var(--tinta) !important; }
header[data-testid="stHeader"]{ background:transparent; }
[data-testid="stMainBlockContainer"]{ padding-top:1.4rem; padding-bottom:4rem; max-width:1320px; }

/* tipografia */
h1, h2, h3{ color:var(--tinta); letter-spacing:-.02em; font-weight:600 !important; }
h3{ font-size:1.15rem !important; }
p, li, label{ line-height:1.55; }

/* ── Sidebar: a "caixa de emenda" azul-noite ───────────────────────────── */
[data-testid="stSidebar"]{
  background:
    radial-gradient(120% 60% at 0% 100%, rgba(68,238,103,.10), transparent 60%),
    linear-gradient(180deg, var(--noite) 0%, var(--abismo) 100%) !important;
  border-right:0;
}
[data-testid="stSidebarNav"] a{
  border-radius:var(--raio-p); margin:2px 6px; padding:.45rem .7rem;
  transition:background .2s ease;
}
[data-testid="stSidebarNav"] a:hover{ background:rgba(255,255,255,.07); }
[data-testid="stSidebarNav"] a[aria-current="page"]{
  background:rgba(68,238,103,.12);
  box-shadow: inset 3px 0 0 var(--verde);
}
[data-testid="stSidebarNav"] a span{ color:#E6EAFF !important; }
[data-testid="stSidebarNavSeparator"]{ border-color:rgba(255,255,255,.12); }
[data-testid="stSidebarHeader"] img, [data-testid="stLogo"]{ height:34px !important; }
.pav-usuario{
  margin:1rem .4rem 0; padding:.85rem 1rem; border-radius:var(--raio-m);
  background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.09);
  color:#C9D0F5; font-size:.82rem;
}
.pav-usuario b{ display:block; color:#fff; font-weight:500; font-size:.95rem; }
.pav-usuario i{
  display:inline-block; width:7px; height:7px; border-radius:50%;
  background:var(--verde); margin-right:.45rem; font-style:normal;
  box-shadow:0 0 0 4px rgba(68,238,103,.15);
}

/* ── Cabeçalho de página ───────────────────────────────────────────────── */
.pav-cab{
  position:relative; overflow:hidden; border-radius:var(--raio-g);
  padding:1.6rem 1.9rem 1.5rem; margin-bottom:1.4rem;
  background:linear-gradient(115deg, var(--noite) 0%, var(--noite-2) 70%, #13308F 100%);
  color:#fff; isolation:isolate;
}
.pav-cab::after{ /* o círculo verde do logo, deslocado */
  content:""; position:absolute; right:8%; top:-128px; width:160px; height:160px;
  border-radius:50%; background:var(--verde); opacity:.92; z-index:-1;
}
.pav-cab svg{ position:absolute; inset:auto 0 0 0; width:100%; height:46px; z-index:-1; opacity:.55; }
.pav-cab h1{ color:#fff !important; font-size:clamp(1.45rem, 2.4vw, 2rem) !important; margin:0 !important; padding:0 !important; }
.pav-cab p{ color:#C9D0F5; margin:.35rem 0 0; max-width:62ch; font-weight:300; }

/* ── Pills viram um seletor segmentado ─────────────────────────────────── */
[data-testid="stButtonGroup"]{ margin-bottom:.6rem; }
[data-testid="stBaseButton-pills"], [data-testid="stBaseButton-pillsActive"]{
  border-radius:999px !important; padding:.45rem 1rem !important; min-height:0 !important;
  font-weight:500 !important; transition:background .2s, color .2s, border-color .2s;
}
[data-testid="stBaseButton-pills"]{ background:var(--cartao) !important; border:1px solid var(--linha) !important; color:var(--nevoa) !important; }
[data-testid="stBaseButton-pills"]:hover{ border-color:var(--verde) !important; color:var(--tinta) !important; }
[data-testid="stBaseButton-pillsActive"]{
  background:var(--verde) !important; border:1px solid var(--verde) !important; color:var(--noite) !important;
}

/* ── Formulários e contêineres ─────────────────────────────────────────── */
[data-testid="stForm"]{
  background:var(--cartao); border:1px solid var(--linha) !important;
  border-radius:var(--raio-g); padding:1.6rem 1.6rem 1.2rem; box-shadow:var(--sombra);
}
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) { border-radius:var(--raio-m); }
[data-testid="stExpander"] details{
  border:1px solid var(--linha); border-radius:var(--raio-m); background:var(--cartao);
}
[data-testid="stExpander"] summary:hover{ color:var(--verde); }
[data-testid="stWidgetLabel"] p{ font-weight:500; font-size:.86rem; color:var(--tinta); }

input, textarea, [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="textarea"]{
  border-radius:var(--raio-p) !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within, [data-baseweb="textarea"]:focus-within{
  border-color:var(--verde) !important; box-shadow:0 0 0 3px rgba(68,238,103,.18) !important;
}
[data-baseweb="tag"]{ background:var(--noite-2) !important; border-radius:999px !important; }
[data-baseweb="tag"] span{ color:#fff !important; }

/* ── Botões ────────────────────────────────────────────────────────────── */
.stButton > button, .stFormSubmitButton > button, [data-testid="stPageLink"] a{
  border-radius:999px !important; font-weight:500 !important; padding:.55rem 1.3rem !important;
  transition:transform .15s ease, box-shadow .2s ease, background .2s ease;
}
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--verde) !important; color:var(--noite) !important; border:0 !important; font-weight:600 !important;
  box-shadow:0 8px 24px -12px rgba(68,238,103,.7);
}
[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover{
  background:#6BF488 !important; transform:translateY(-1px);
}
[data-testid="stBaseButton-primary"]:active, [data-testid="stBaseButton-primaryFormSubmit"]:active{ transform:translateY(1px) scale(.98); }
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"]{
  background:var(--cartao) !important; color:var(--tinta) !important; border:1px solid var(--linha) !important;
}
button:focus-visible, a:focus-visible{ outline:3px solid var(--ciano) !important; outline-offset:2px; }

/* ── Tabelas / dataframes / métricas ───────────────────────────────────── */
[data-testid="stDataFrame"], [data-testid="stDataEditor"]{
  border:1px solid var(--linha); border-radius:var(--raio-m); overflow:hidden; background:var(--cartao);
}
[data-testid="stMetric"]{
  background:#fff; border:1px solid var(--linha); border-radius:var(--raio-m);
  padding:1rem 1.1rem; box-shadow:var(--sombra);
}
[data-testid="stMetricValue"]{ color:var(--tinta); font-weight:600; }
[data-testid="stAlert"]{ border-radius:var(--raio-m); }
hr{ border-color:var(--linha) !important; }

/* ── Dialog ────────────────────────────────────────────────────────────── */
[data-testid="stDialog"] [role="dialog"]{ border-radius:var(--raio-g); border-top:4px solid var(--verde); }

/* ── Componentes próprios ──────────────────────────────────────────────── */
.pav-resumo{ display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:.8rem; margin:.4rem 0 1.4rem; }
.pav-num{
  background:var(--cartao); border:1px solid var(--linha); border-radius:var(--raio-m);
  padding:1rem 1.1rem .9rem; position:relative; overflow:hidden; box-shadow:var(--sombra);
}
.pav-num::before{ content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--tom, var(--noite)); }
.pav-num span{ font-size:.8rem; color:var(--nevoa); }
.pav-num b{ display:block; font-size:1.9rem; font-weight:600; color:var(--tinta); line-height:1.15; margin-top:.15rem; }
.pav-num.destaque{ background:var(--noite); border-color:var(--noite); }
.pav-num.destaque span{ color:#C9D0F5; } .pav-num.destaque b{ color:#fff; }
.pav-num.destaque::before{ background:var(--verde); }

.pav-pessoa{
  background:var(--cartao); border:1px solid var(--linha); border-radius:var(--raio-m);
  padding:1rem 1.1rem; margin-bottom:.8rem; box-shadow:var(--sombra);
}
.pav-pessoa header{ display:flex; justify-content:space-between; align-items:baseline; gap:.6rem; margin-bottom:.7rem; }
.pav-pessoa header strong{ font-weight:600; color:var(--tinta); overflow-wrap:anywhere; }
.pav-pessoa header em{ font-style:normal; font-size:1.4rem; font-weight:600; color:var(--verde); }
.pav-barras{ display:grid; gap:.45rem; }
.pav-barra{ display:grid; grid-template-columns:7.5rem 1fr 2rem; align-items:center; gap:.5rem; font-size:.8rem; color:var(--nevoa); }
.pav-barra i{ display:block; height:6px; border-radius:6px; background:var(--cartao-2); overflow:hidden; }
.pav-barra i u{ display:block; height:100%; border-radius:6px; background:var(--tom); transform-origin:left; }
.pav-barra b{ text-align:right; color:var(--tinta); font-weight:500; }

.pav-bloco{ background:var(--cartao); border:1px solid var(--linha); border-radius:var(--raio-m); padding:1rem 1.1rem; height:100%; box-shadow:var(--sombra); }
.pav-bloco h4{ margin:0 0 .7rem; font-size:.95rem; font-weight:600; color:var(--tinta); }
.pav-chips{ display:flex; flex-wrap:wrap; gap:.4rem; }
.pav-chip{ font-size:.8rem; padding:.3rem .7rem; border-radius:999px; background:var(--cartao-2); color:var(--tinta); border:1px solid transparent; overflow-wrap:anywhere; }
.pav-chip.verde{ background:rgba(68,238,103,.14); color:#7CF79A; }
.pav-chip.ciano{ background:rgba(0,167,225,.14); color:#6FD3F7; }
.pav-chip.noite{ background:var(--noite); color:#fff; }
.pav-chip.ambar{ background:rgba(242,165,65,.14); color:#F7C27A; }
.pav-lista{ list-style:none; padding:0 !important; margin:0 !important; display:grid; gap:.5rem; }
.pav-lista li{ margin:0 !important; font-size:.86rem; padding:.55rem .7rem; border-radius:var(--raio-p); background:var(--cartao-2); border-left:3px solid var(--tom, var(--ciano)); overflow-wrap:anywhere; }
.pav-dados{ display:grid; gap:.55rem; }
.pav-dados div{ display:flex; justify-content:space-between; font-size:.88rem; color:var(--nevoa); border-bottom:1px dashed var(--linha); padding-bottom:.4rem; }
.pav-dados b{ color:var(--tinta); font-weight:600; }

.pav-vazio{
  border:1.5px dashed var(--linha); border-radius:var(--raio-g); padding:2.2rem 1.6rem;
  text-align:center; background:var(--cartao); color:var(--nevoa);
}
.pav-vazio strong{ display:block; color:var(--tinta); font-size:1.05rem; font-weight:600; margin-bottom:.3rem; }

.pav-atalhos{ display:grid; grid-template-columns:repeat(auto-fit, minmax(230px,1fr)); gap:.8rem; margin-top:.2rem; }

@media (max-width: 640px){
  [data-testid="stMainBlockContainer"]{ padding-left:.9rem; padding-right:.9rem; padding-top:1rem; }
  .pav-cab{ padding:1.2rem 1.2rem 1.1rem; }
  .pav-cab::after{ width:140px; height:140px; right:-40px; top:-50px; }
  [data-testid="stForm"]{ padding:1.1rem; }
  .pav-num b{ font-size:1.5rem; }
}
@media (prefers-reduced-motion: reduce){
  *{ transition:none !important; animation:none !important; }
}
</style>
"""


def _fibra_svg() -> str:
    """Linhas de fibra discretas na base do cabeçalho (estático)."""
    return (
        '<svg viewBox="0 0 1200 46" preserveAspectRatio="none" aria-hidden="true">'
        '<path d="M0 30 C 300 5, 520 44, 820 20 S 1100 8, 1200 26" fill="none" stroke="#44EE67" stroke-width="1.4"/>'
        '<path d="M0 40 C 260 22, 600 46, 880 30 S 1120 22, 1200 36" fill="none" stroke="#00A7E1" stroke-width="1"/>'
        '<path d="M0 20 C 340 40, 640 10, 940 34 S 1150 30, 1200 14" fill="none" stroke="#ffffff" stroke-opacity=".35" stroke-width=".8"/>'
        "</svg>"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entrada orquestrada (GSAP no documento pai, uma vez por página)
# ─────────────────────────────────────────────────────────────────────────────
def _movimento(pagina: str):
    pagina_js = pagina.replace("'", "")
    html = f"""
<script>
(function(){{
  let P, D;
  try {{ P = window.parent; D = P.document; P.__pavTeste = 1; }} catch (e) {{ return; }}
  if (P.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (P.__pavPagina === '{pagina_js}') return;   // reruns não re-animam
  P.__pavPagina = '{pagina_js}';

  function rodar(){{
    const g = P.gsap;
    const raiz = D.querySelector('[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]');
    if (!raiz) return;
    const itens = Array.from(raiz.children).filter(el => el.offsetHeight > 4).slice(0, 10);
    g.fromTo(itens, {{autoAlpha:0, y:14}},
      {{autoAlpha:1, y:0, duration:.55, ease:'power2.out', stagger:.06, clearProps:'transform,opacity,visibility'}});
    const barras = D.querySelectorAll('.pav-barra u');
    if (barras.length) g.from(barras, {{scaleX:0, duration:.9, ease:'power3.out', stagger:.02, delay:.25}});
    D.querySelectorAll('.pav-num b[data-n]').forEach(el => {{
      const alvo = +el.dataset.n, o = {{v:0}};
      g.to(o, {{v:alvo, duration:1, ease:'power2.out', delay:.2,
        onUpdate:() => el.textContent = Math.round(o.v).toLocaleString('pt-BR')}});
    }});
  }}
  function aguardar(n){{
    if (P.gsap) return setTimeout(rodar, 60);
    if (n > 40) return;
    setTimeout(() => aguardar(n+1), 50);
  }}
  if (!P.gsap && !D.getElementById('pav-gsap')) {{
    const s = D.createElement('script'); s.id = 'pav-gsap'; s.src = '{GSAP_CDN}';
    D.head.appendChild(s);
  }}
  aguardar(0);
}})();
</script>
"""
    with st.container(key="pav-movimento"):
        _iframe(html, 1)


def aplicar_tema(pagina: str, animar: bool = True):
    """Aplica CSS, logo e (opcional) a entrada animada. Chamar logo após set_page_config."""
    if st.session_state.get("authenticated"):
        # o login abre com a sidebar recolhida; depois de entrar ela volta aberta
        st.set_page_config(initial_sidebar_state="expanded")
    st.markdown(_CSS, unsafe_allow_html=True)
    if st.session_state.get("authenticated"):
        st.markdown(
            "<style>[data-testid='stSidebar']{display:flex !important;visibility:visible !important}</style>",
            unsafe_allow_html=True,
        )
    if st.session_state.get("authenticated"):
        st.logo(LOGO_NEGATIVO, size="large", icon_image=LOGO_NEGATIVO)
        with st.sidebar:
            usuario = escape(str(st.session_state.get("username", "")))
            perfil = escape(str(st.session_state.get("role", "")).capitalize())
            st.markdown(
                f'<div class="pav-usuario"><i></i>{perfil}<b>{usuario}</b></div>',
                unsafe_allow_html=True,
            )
    if animar:
        _movimento(pagina)
    # o iframe de movimento é invisível e não ocupa espaço
    st.markdown("<style>.st-key-pav-movimento{display:none !important}</style>", unsafe_allow_html=True)


def cabecalho(titulo: str, descricao: str = ""):
    desc = f"<p>{escape(descricao)}</p>" if descricao else ""
    st.markdown(
        f'<div class="pav-cab">{_fibra_svg()}<h1>{escape(titulo)}</h1>{desc}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hero de fibra óptica — Three.js (shader) + GSAP
# ─────────────────────────────────────────────────────────────────────────────
def hero_fibra(titulo: str, subtitulo: str = "", altura: int = 260, rodape: str = ""):
    t, s, r = escape(titulo), escape(subtitulo), escape(rodape)
    _iframe(
        f"""
<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap" rel="stylesheet">
<style>
  html,body{{margin:0;height:100%;background:transparent;overflow:hidden;font-family:'Lexend',system-ui,sans-serif}}
  #cena{{position:absolute;inset:0;border-radius:20px;overflow:hidden;
         background:radial-gradient(90% 120% at 85% 10%, #13308F 0%, #001059 55%, #000A3B 100%)}}
  canvas{{display:block;width:100%;height:100%}}
  .txt{{position:absolute;left:clamp(20px,4vw,44px);bottom:clamp(20px,3.5vw,38px);right:20px;color:#fff;pointer-events:none}}
  h1{{margin:0;font-weight:600;font-size:clamp(26px,4.2vw,50px);line-height:1.04;letter-spacing:-.03em;max-width:15ch}}
  p{{margin:.7rem 0 0;color:#C9D0F5;font-weight:300;font-size:clamp(13px,1.3vw,16px);max-width:46ch}}
  small{{position:absolute;top:clamp(18px,3vw,30px);left:clamp(20px,4vw,44px);color:#44EE67;font-size:13px;display:flex;align-items:center;gap:8px}}
  small::before{{content:"";width:8px;height:8px;border-radius:50%;background:#44EE67;box-shadow:0 0 0 5px rgba(68,238,103,.18)}}
  .linha{{display:block;overflow:hidden}} .linha span{{display:inline-block}}
</style></head><body>
<div id="cena"></div>
{('<small>'+r+'</small>') if r else ''}
<div class="txt">
  <h1 id="tit">{t}</h1>{('<p id="sub">'+s+'</p>') if s else ''}
</div>
<script src="{THREE_CDN}"></script>
<script src="{GSAP_CDN}"></script>
<script>
(function(){{
  const reduz = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const box = document.getElementById('cena');
  if (!window.THREE) return;
  const W = () => box.clientWidth, H = () => box.clientHeight;

  const renderer = new THREE.WebGLRenderer({{antialias:true, alpha:true}});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(W(), H());
  box.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(38, W()/H(), .1, 100);
  cam.position.set(0, 0, 9);

  // Cada fio é uma curva CatmullRom convertida em tubo fino; o shader
  // desenha pulsos de luz que viajam ao longo do comprimento (uv.x).
  const vert = `
    varying vec2 vUv;
    void main(){{ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }}`;
  const frag = `
    uniform float uT; uniform vec3 uCor; uniform float uVel; uniform float uFase; uniform float uBrilho;
    varying vec2 vUv;
    void main(){{
      float base = 0.10 + 0.05 * sin(vUv.x * 30.0);
      float p = fract(vUv.x * 1.6 - uT * uVel + uFase);
      float pulso = smoothstep(0.0, 0.10, p) * (1.0 - smoothstep(0.10, 0.34, p));
      float p2 = fract(vUv.x * 3.1 - uT * uVel * 0.7 + uFase * 2.3);
      float faisca = pow(1.0 - abs(p2 - 0.5) * 2.0, 18.0) * 0.8;
      float borda = 1.0 - abs(vUv.y - 0.5) * 2.0;
      float a = (base + pulso * 1.1 + faisca) * uBrilho * (0.55 + 0.45 * borda);
      gl_FragColor = vec4(uCor * (0.6 + pulso + faisca), a);
    }}`;

  const cores = [new THREE.Color('#44EE67'), new THREE.Color('#00A7E1'), new THREE.Color('#9AA8FF')];
  const grupo = new THREE.Group(); scene.add(grupo);
  const mats = [];
  const N = innerWidth < 640 ? 14 : 24;
  for (let i = 0; i < N; i++){{
    const y0 = (i / N - .5) * 5.2, z = (Math.random() - .5) * 3;
    const pts = [];
    for (let k = 0; k <= 6; k++){{
      const x = -9 + k * 3;
      pts.push(new THREE.Vector3(x, y0 + Math.sin(k * .9 + i * .7) * (.35 + Math.random() * .5) + (k/6) * 1.4 - .7, z + Math.cos(k + i) * .6));
    }}
    const curva = new THREE.CatmullRomCurve3(pts);
    const geo = new THREE.TubeGeometry(curva, 180, .012 + Math.random() * .018, 6, false);
    const cor = i % 5 === 0 ? cores[0] : (i % 3 === 0 ? cores[2] : cores[1]);
    const mat = new THREE.ShaderMaterial({{
      vertexShader: vert, fragmentShader: frag, transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {{ uT:{{value:0}}, uCor:{{value:cor}}, uVel:{{value:.12 + Math.random() * .22}},
                   uFase:{{value:Math.random()}}, uBrilho:{{value:0}} }}
    }});
    mats.push(mat);
    grupo.add(new THREE.Mesh(geo, mat));
  }}
  grupo.rotation.z = -.12;

  // Entrada: fios acendem em sequência, título sobe
  const tl = gsap.timeline({{defaults:{{ease:'power3.out'}}}});
  tl.to(mats.map(m => m.uniforms.uBrilho), {{value:1, duration:1.4, stagger:.035}}, 0)
    .from('#tit', {{y:24, autoAlpha:0, duration:.9}}, .2)
    .from('#sub', {{y:14, autoAlpha:0, duration:.8}}, .38)
    .from('small', {{autoAlpha:0, duration:.6}}, .5);
  if (reduz) tl.progress(1);

  // Parallax suave com o ponteiro (quickTo evita criar tweens por evento)
  const rx = gsap.quickTo(grupo.rotation, 'x', {{duration:1.2, ease:'power3'}});
  const ry = gsap.quickTo(grupo.rotation, 'y', {{duration:1.2, ease:'power3'}});
  if (!reduz) addEventListener('pointermove', e => {{
    rx((e.clientY / H() - .5) * .18); ry((e.clientX / W() - .5) * .28);
  }});

  let ativo = true;
  new IntersectionObserver(([e]) => ativo = e.isIntersecting).observe(box);
  document.addEventListener('visibilitychange', () => ativo = !document.hidden);

  const relogio = new THREE.Clock();
  gsap.ticker.add(() => {{
    if (!ativo) return;
    const t = reduz ? 2.0 : relogio.getElapsedTime();
    for (const m of mats) m.uniforms.uT.value = t;
    renderer.render(scene, cam);
  }});

  new ResizeObserver(() => {{
    renderer.setSize(W(), H()); cam.aspect = W()/H(); cam.updateProjectionMatrix();
  }}).observe(box);
}})();
</script></body></html>
""",
        altura,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Blocos de conteúdo
# ─────────────────────────────────────────────────────────────────────────────
def resumo_numeros(itens):
    """itens: lista de (rótulo, valor, cor_css | 'destaque')."""
    html = []
    for rotulo, valor, tom in itens:
        classe = "pav-num destaque" if tom == "destaque" else "pav-num"
        estilo = "" if tom == "destaque" else f' style="--tom:{tom}"'
        try:
            n = int(valor)
            num = f'<b data-n="{n}">{n:,}</b>'.replace(",", ".")
        except (TypeError, ValueError):
            num = f"<b>{escape(str(valor))}</b>"
        html.append(f'<div class="{classe}"{estilo}><span>{escape(rotulo)}</span>{num}</div>')
    st.markdown(f'<div class="pav-resumo">{"".join(html)}</div>', unsafe_allow_html=True)


TIPOS_ACAO = [
    ("Visita", "Visitas", CORES["verde"]),
    ("Acao de Vendas", "Ações de vendas", CORES["ciano"]),
    ("Lead", "Leads", "#7C6CFF"),
    ("Ficha Cadastro", "Fichas de cadastro", "#F2A541"),
]


def cartao_executivo(nome: str, valores: dict, maximo: int):
    total = sum(int(valores.get(k, 0)) for k, _, _ in TIPOS_ACAO)
    barras = []
    for chave, rotulo, cor in TIPOS_ACAO:
        v = int(valores.get(chave, 0))
        pct = 0 if maximo <= 0 else max(v / maximo * 100, 2 if v else 0)
        barras.append(
            f'<div class="pav-barra"><span>{rotulo}</span>'
            f'<i><u style="width:{pct:.1f}%;--tom:{cor}"></u></i><b>{v}</b></div>'
        )
    st.markdown(
        f'<article class="pav-pessoa"><header><strong>{escape(str(nome))}</strong>'
        f'<em title="Total de ações">{total}</em></header>'
        f'<div class="pav-barras">{"".join(barras)}</div></article>',
        unsafe_allow_html=True,
    )


def bloco_chips(titulo: str, itens, tom: str = "", vazio: str = "Nada registrado."):
    corpo = (
        '<div class="pav-chips">'
        + "".join(f'<span class="pav-chip {tom}">{escape(str(i))}</span>' for i in itens)
        + "</div>"
        if itens
        else f'<span style="color:var(--nevoa);font-size:.85rem">{escape(vazio)}</span>'
    )
    st.markdown(f'<div class="pav-bloco"><h4>{escape(titulo)}</h4>{corpo}</div>', unsafe_allow_html=True)


def bloco_lista(titulo: str, itens, cor: str = CORES["ciano"], vazio: str = "Nada registrado."):
    corpo = (
        f'<ul class="pav-lista" style="--tom:{cor}">'
        + "".join(f"<li>{escape(str(i))}</li>" for i in itens)
        + "</ul>"
        if itens
        else f'<span style="color:var(--nevoa);font-size:.85rem">{escape(vazio)}</span>'
    )
    st.markdown(f'<div class="pav-bloco"><h4>{escape(titulo)}</h4>{corpo}</div>', unsafe_allow_html=True)


def bloco_dados(titulo: str, pares):
    linhas = "".join(f"<div><span>{escape(str(k))}</span><b>{escape(str(v))}</b></div>" for k, v in pares)
    st.markdown(
        f'<div class="pav-bloco"><h4>{escape(titulo)}</h4><div class="pav-dados">{linhas}</div></div>',
        unsafe_allow_html=True,
    )


def estado_vazio(titulo: str, texto: str = ""):
    st.markdown(
        f'<div class="pav-vazio"><strong>{escape(titulo)}</strong>{escape(texto)}</div>',
        unsafe_allow_html=True,
    )


# CSS extra injetado na página de contatos (HTML standalone em iframe)
CSS_CONTATOS = """
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{color-scheme:dark;--paper:#050608;--ink:#EEF1FF;--mute:#98A1CF;--line:#222846;--fiber:#44EE67;--ok:#44EE67;--warn:#F2A541;--bad:#FF6B5B;--card:#0E1120}
body{font-family:'Lexend',system-ui,sans-serif !important}
h1,th,aside h3,.kpi b{font-family:'Lexend',system-ui,sans-serif !important}
header{border-bottom:0 !important;background:linear-gradient(115deg,#001059,#0B1D78);color:#fff;border-radius:18px;margin:4px 4px 0}
header h1{color:#fff}header h1 span{color:#44EE67}header .sub{color:#C9D0F5}
header .kpis{border-color:rgba(255,255,255,.25);border-radius:12px;overflow:hidden}
header .kpi{border-color:rgba(255,255,255,.2)}header .kpi small{color:#C9D0F5}
header .kpi:hover{background:rgba(255,255,255,.08)}
input[type=search],select,button{border-color:var(--line) !important;border-radius:8px !important;color:var(--ink)}
button.pri{background:#44EE67 !important;color:#001059 !important}
button:hover{background:#44EE67 !important;color:#001059 !important;border-color:#44EE67 !important}
.seg{border-color:var(--line) !important;border-radius:999px;overflow:hidden}
.seg button{border-radius:0 !important}.seg button.on{background:#44EE67 !important;color:#001059 !important}
table{border-radius:12px;overflow:hidden}
tr:hover td{background:#141830}
</style>
"""
