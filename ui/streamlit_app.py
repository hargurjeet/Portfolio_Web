import streamlit as st
import requests
import base64
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/chat")
RESUME_PATH = "data/Hargurjeet_Lead_GenAI_Specialist.pdf"

st.set_page_config(
    page_title="Hargurjeet · AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

# ── THEME STATE ────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark = st.session_state.dark_mode

# ── THEME VARIABLES ────────────────────────────────────────────────────────────
if dark:
    bg          = "#0f0f0f"
    sidebar_bg  = "#141414"
    card_bg     = "#1a1a1a"
    card_border = "#252525"
    text_main   = "#f0f0f0"
    text_body   = "#e0e0e0"
    text_muted  = "#888888"
    text_dim    = "#555555"
    input_bg    = "#1a1a1a"
    input_bdr   = "#333333"
    hr_color    = "#222222"
    hover_bg    = "#222222"
    tab_bg      = "#1a1a1a"
    tab_border  = "#2a2a2a"
    expander_bg = "#161616"
    tag_bg      = "#252525"
    tag_color   = "#888888"
    tag_border  = "#333333"
    blog_bg     = "#141414"
    blog_bdr    = "#222222"
    project_bg  = "#141414"
    toggle_icon = "☀️"
    toggle_lbl  = "Light Mode"
    scrollbar_track = "#0f0f0f"
    scrollbar_thumb = "#333333"
else:
    bg          = "#f5f5f0"
    sidebar_bg  = "#ffffff"
    card_bg     = "#ffffff"
    card_border = "#e0e0e0"
    text_main   = "#1a1a1a"
    text_body   = "#2a2a2a"
    text_muted  = "#666666"
    text_dim    = "#999999"
    input_bg    = "#ffffff"
    input_bdr   = "#d0d0d0"
    hr_color    = "#e8e8e8"
    hover_bg    = "#f0f0f0"
    tab_bg      = "#ececec"
    tab_border  = "#d8d8d8"
    expander_bg = "#f9f9f9"
    tag_bg      = "#eeeeee"
    tag_color   = "#555555"
    tag_border  = "#d0d0d0"
    blog_bg     = "#ffffff"
    blog_bdr    = "#e0e0e0"
    project_bg  = "#ffffff"
    toggle_icon = "🌙"
    toggle_lbl  = "Dark Mode"
    scrollbar_track = "#f5f5f0"
    scrollbar_thumb = "#cccccc"

accent = "#ff5733"

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
html, body, [class*="css"] {{
    font-family: 'Comic Sans MS', 'Comic Sans', 'Chalkboard SE', cursive !important;
    font-size: 17px;
    -webkit-font-smoothing: antialiased;
}}

.stApp {{
    background-color: {bg};
    color: {text_body};
}}

[data-testid="stSidebar"] {{
    background-color: {sidebar_bg};
    border-right: 1px solid {hr_color};
    display: block !important;
    visibility: visible !important;
    min-width: 270px !important;
    max-width: 270px !important;
    transform: none !important;
}}
[data-testid="stSidebar"] * {{
    color: {text_body} !important;
    font-family: 'Comic Sans MS', 'Comic Sans', cursive !important;
}}

#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0 !important; min-height: 0 !important;
    visibility: hidden !important;
}}
[data-testid="stToolbar"] {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
button[kind="header"] {{ display: none !important; }}

.stTabs [data-baseweb="tab-list"] {{
    background-color: {tab_bg};
    border-radius: 12px;
    padding: 4px; gap: 4px;
    border: 1px solid {tab_border};
}}
.stTabs [data-baseweb="tab"] {{
    background-color: transparent;
    color: {text_muted} !important;
    border-radius: 8px;
    font-family: 'Comic Sans MS', cursive !important;
    font-weight: 600;
    font-size: 16px;
    padding: 10px 22px;
    transition: all 0.2s ease;
}}
.stTabs [aria-selected="true"] {{
    background-color: {accent} !important;
    color: #fff !important;
}}

[data-testid="stChatMessage"] {{
    background-color: {card_bg} !important;
    border: 1px solid {card_border};
    border-radius: 16px !important;
    padding: 16px 22px !important;
    margin-bottom: 10px;
}}
[data-testid="stChatMessage"] p {{
    font-size: 17px !important;
    line-height: 1.85 !important;
    color: {text_body} !important;
    font-family: 'Comic Sans MS', cursive !important;
}}

[data-testid="stChatInput"] {{
    background-color: {input_bg} !important;
    border: 1px solid {input_bdr} !important;
    border-radius: 14px !important;
    color: {text_body} !important;
    font-size: 16px !important;
    font-family: 'Comic Sans MS', cursive !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 2px rgba(255, 87, 51, 0.15) !important;
}}

[data-testid="stExpander"] {{
    background-color: {expander_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{
    font-size: 14px !important;
    color: {text_muted} !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

div[data-testid="stHorizontalBlock"] .stButton > button {{
    background-color: {card_bg} !important;
    color: {text_muted} !important;
    border: 1px solid {card_border} !important;
    border-radius: 20px !important;
    font-size: 15px !important;
    padding: 10px 18px !important;
    font-family: 'Comic Sans MS', cursive !important;
    transition: all 0.2s ease;
}}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
    background-color: {hover_bg} !important;
    color: {accent} !important;
    border-color: {accent} !important;
}}

.stButton > button {{
    background-color: transparent;
    color: {accent} !important;
    border: 1px solid {accent} !important;
    border-radius: 10px;
    font-family: 'Comic Sans MS', cursive !important;
    font-weight: 600;
    font-size: 15px;
    padding: 8px 18px;
    transition: all 0.2s ease;
    width: 100%;
}}
.stButton > button:hover {{
    background-color: {accent} !important;
    color: #fff !important;
}}
.stDownloadButton > button {{
    background-color: {accent} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px;
    font-family: 'Comic Sans MS', cursive !important;
    font-weight: 600;
    font-size: 16px;
    width: 100%;
    padding: 12px;
}}

hr {{ border-color: {hr_color} !important; margin: 16px 0; }}

::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {scrollbar_track}; }}
::-webkit-scrollbar-thumb {{ background: {scrollbar_thumb}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {accent}; }}

[data-testid="stSpinner"] {{ color: {accent} !important; }}

.stCaption, [data-testid="stCaptionContainer"] {{
    color: {text_dim} !important;
    font-size: 13px !important;
}}

.stMarkdown, .stMarkdown p, .stMarkdown li {{
    font-family: 'Comic Sans MS', cursive !important;
    color: {text_body};
}}

/* ── Typing indicator ── */
.thinking-dots {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 2px;
}}
.thinking-dots span {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {accent};
    display: inline-block;
    animation: bounce 1.2s infinite ease-in-out;
}}
.thinking-dots span:nth-child(1) {{ animation-delay: 0s; }}
.thinking-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
.thinking-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes bounce {{
    0%, 80%, 100% {{ transform: scale(0.6); opacity: 0.4; }}
    40% {{ transform: scale(1.0); opacity: 1; }}
}}

/* ── Follow-up chips ── */

/* ── Hide sidebar collapse button ── */
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}
button[title="keyboard_double_arrow_left"],
button[title="keyboard_double_arrow_right"] {{
    display: none !important;
}}

</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
AVATAR_PATH = "data/my_avatar.png"

with st.sidebar:
    # Read and encode the photo
    if os.path.exists(AVATAR_PATH):
        with open(AVATAR_PATH, "rb") as img_file:
            avatar_b64 = base64.b64encode(img_file.read()).decode("utf-8")
        avatar_html = f'<img src="data:image/png;base64,{avatar_b64}" style="width:180px;height:180px;border-radius:50%;object-fit:cover;border:3px solid {accent};box-shadow:0 6px 24px rgba(255,87,51,0.3);">'
    else:
        # Fallback to letter avatar if photo not found
        avatar_html = f'<div style="width:180px;height:180px;background:linear-gradient(135deg,#ff5733,#ff8c42);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:700;color:#fff;font-family:Comic Sans MS,cursive;">H</div>'

    st.markdown(f"""
    <div style="text-align: center; padding: 28px 0 20px 0;">
        <div style="margin: 0 auto 16px auto; width:180px;">
            {avatar_html}
        </div>
        <div style="font-family: Comic Sans MS, cursive; font-size: 21px; color: {text_main}; margin-bottom: 6px; font-weight: 700;">
            Hargurjeet Singh
        </div>
        <div style="font-size: 12px; color: {accent}; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; font-family: Comic Sans MS, cursive;">
            Lead GenAI Specialist
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── THEME TOGGLE BUTTON ────────────────────────────────────────────────────
    if st.button(f"{toggle_icon}  {toggle_lbl}"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding: 0 6px;">
        <div style="font-size: 11px; color: {text_dim}; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 14px; font-weight: 700; font-family: Comic Sans MS, cursive;">Connect</div>
        <a href="https://www.linkedin.com/in/hargurjeet/" target="_blank" style="display:flex;align-items:center;gap:12px;color:{text_muted};text-decoration:none;font-size:15px;padding:10px 12px;border-radius:10px;font-family:Comic Sans MS,cursive;margin-bottom:4px;" onmouseover="this.style.background='{hover_bg}'" onmouseout="this.style.background='transparent'">
            🔗 &nbsp;LinkedIn
        </a>
        <a href="https://github.com/hargurjeet" target="_blank" style="display:flex;align-items:center;gap:12px;color:{text_muted};text-decoration:none;font-size:15px;padding:10px 12px;border-radius:10px;font-family:Comic Sans MS,cursive;margin-bottom:4px;" onmouseover="this.style.background='{hover_bg}'" onmouseout="this.style.background='transparent'">
            🐙 &nbsp;GitHub
        </a>
        <a href="mailto:gurjeet333@gmail.com" style="display:flex;align-items:center;gap:12px;color:{text_muted};text-decoration:none;font-size:15px;padding:10px 12px;border-radius:10px;font-family:Comic Sans MS,cursive;" onmouseover="this.style.background='{hover_bg}'" onmouseout="this.style.background='transparent'">
            ✉️ &nbsp;Email
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Profile label
    st.markdown(f'<div style="font-size:11px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;font-weight:700;font-family:Comic Sans MS,cursive;padding:0 6px;">Profile</div>', unsafe_allow_html=True)

    # Stat rows - each as its own call to avoid f-string conflicts
    for icon, label, value in [
        ("🏢", "Experience", "15+ years"),
        ("📍", "Location", "Bangalore"),
        ("🎓", "Degree", "M.S. ML & AI"),
        ("☁️", "Cloud", "AWS · GCP"),
    ]:
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 6px;">'
            f'<span style="color:{text_muted};font-size:14px;font-family:Comic Sans MS,cursive;">{icon} {label}</span>'
            f'<span style="color:{accent};font-weight:700;font-size:14px;font-family:Comic Sans MS,cursive;">{value}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(f'<div style="border-top:1px solid {hr_color};margin:12px 6px;"></div>', unsafe_allow_html=True)

    # Core stack chips
    st.markdown(f'<div style="font-size:11px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;font-weight:700;margin-bottom:8px;font-family:Comic Sans MS,cursive;padding:0 6px;">Core Stack</div>', unsafe_allow_html=True)
    skills = ["LangChain", "RAG", "LLMs", "Python", "AWS Bedrock", "FastAPI", "FAISS", "MLOps", "XGBoost", "CrewAI"]
    chips_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;padding:0 6px;">' + "".join(
        f'<span style="background:{tag_bg};color:{text_muted};font-size:11px;font-family:JetBrains Mono,monospace;padding:3px 8px;border-radius:4px;">{s}</span>'
        for s in skills
    ) + '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🗑️  Clear Conversation"):
        st.session_state.messages = []
        st.session_state.sources = {}
        st.rerun()

    st.markdown(f"""
    <div style="text-align:center;margin-top:20px;font-size:12px;color:{text_dim};font-family:Comic Sans MS,cursive;">
        Powered by GPT-4o-mini · LangChain · FAISS
    </div>
    """, unsafe_allow_html=True)


# ── PAGE HEADER ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="padding: 36px 0 24px 0;">
    <div style="font-family: Comic Sans MS, cursive; font-size: 46px; color: {text_main}; line-height: 1.1; font-weight: 700;">
        Ask me anything
    </div>
    <div style="font-size: 18px; color: {text_muted}; margin-top: 8px; font-family: Comic Sans MS, cursive;">
        about Hargurjeet's experience, skills, and background
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
chat_tab, experience_tab, resume_tab, blogs_tab, projects_tab = st.tabs(["💬  Chat", "🧭  Experience", "📄  Resume", "✍️  Blogs", "🚀  Projects"])


# ── TAB 1: CHAT ────────────────────────────────────────────────────────────────
with chat_tab:

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources" not in st.session_state:
        st.session_state.sources = {}
    if "preset_question" not in st.session_state:
        st.session_state.preset_question = None

    def build_chat_history():
        history = []
        msgs = st.session_state.messages
        for i in range(0, len(msgs) - 1, 2):
            if msgs[i]["role"] == "user" and msgs[i + 1]["role"] == "assistant":
                history.append([msgs[i]["content"], msgs[i + 1]["content"]])
        return history

    chat_container = st.container(height=520)
    with chat_container:
        if not st.session_state.messages:
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:280px;gap:12px;">
                <div style="font-size:44px;">⚡</div>
                <div style="font-family:Comic Sans MS,cursive;font-size:24px;color:{text_muted};font-weight:700;">
                    Start a conversation
                </div>
                <div style="font-size:16px;color:{text_dim};text-align:center;max-width:340px;line-height:1.7;font-family:Comic Sans MS,cursive;">
                    Click a suggestion below or type your own question
                </div>
            </div>
            """, unsafe_allow_html=True)

        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Suggestion buttons (only when no messages) ──
    if not st.session_state.messages:
        suggestions = [
            "What's his GenAI experience?",
            "What cloud platforms has he used?",
            "What's his most recent role?",
        ]
        cols = st.columns(len(suggestions))
        for col, suggestion in zip(cols, suggestions):
            with col:
                if st.button(suggestion, use_container_width=True):
                    st.session_state.preset_question = suggestion
                    st.rerun()

    user_input = st.chat_input("Ask anything about Hargurjeet...")
    question = user_input or st.session_state.pop("preset_question", None)

    if question:
        chat_history = build_chat_history()
        st.session_state.messages.append({"role": "user", "content": question})

        try:
            with requests.post(
                API_URL,
                json={"question": question, "chat_history": chat_history},
                stream=True
            ) as response:
                response.raise_for_status()
                full_answer = ""
                sources = []
                got_first_token = False

                with chat_container:
                    with st.chat_message("assistant"):
                        token_placeholder = st.empty()

                        # ── Thinking indicator ──
                        token_placeholder.markdown(
                            f'<div style="display:inline-flex;align-items:center;gap:8px;font-family:Comic Sans MS,cursive;font-size:15px;color:{text_muted};">'
                            f'<span>Thinking</span>'
                            f'<div class="thinking-dots"><span></span><span></span><span></span></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                        for line in response.iter_lines():
                            if not line:
                                continue
                            line = line.decode("utf-8")
                            if not line.startswith("data: "):
                                continue
                            payload = line[len("data: "):]
                            if payload == "[DONE]":
                                break
                            data = json.loads(payload)
                            if "token" in data:
                                if not got_first_token:
                                    got_first_token = True
                                full_answer += data["token"]
                                token_placeholder.markdown(full_answer + "▌")
                            if "sources" in data:
                                sources = data["sources"]

                        token_placeholder.markdown(full_answer)

                assistant_idx = len(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": full_answer})
                st.session_state.sources[assistant_idx] = sources

        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ Could not connect to the API. Make sure FastAPI is running on port 8000."
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Something went wrong: {str(e)}"
            })

        st.rerun()


# ── TAB 2: EXPERIENCE ─────────────────────────────────────────────────────────
with experience_tab:

    st.markdown(f'<div style="font-size:12px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;font-weight:700;margin-bottom:28px;margin-top:8px;font-family:Comic Sans MS,cursive;">🧭 Career Timeline</div>', unsafe_allow_html=True)

    EXPERIENCE = [
        {
            "role": "Senior Data Scientist",
            "company": "British Telecom (BT)",
            "period": "May 2022 – Present",
            "type": "current",
            "logo": "🔵",
            "highlights": [
                "Built RAG-powered conversational chatbot using LLMs, reducing manual data extraction time by 70%",
                "Designed scalable AWS pipelines (Textract, OpenSearch, Bedrock) processing 100K+ multimodal documents at 90%+ accuracy",
                "Implemented multi-step agentic workflows with CrewAI, integrating tool-augmented pipelines with guardrails",
                "Developed LLM evaluation framework (Ragas) covering hallucination, toxicity, bias, answer relevancy",
                "Engineered multi-label recommendation model (XGBoost + Random Forest) — increased SD-WAN sales by 10%",
                "Built market basket / apriori recommendation system — achieved 30% increase in VAS sales",
            ],
            "tags": ["LLMs", "RAG", "CrewAI", "AWS Bedrock", "XGBoost", "Docker", "FastAPI", "Ragas"],
        },
        {
            "role": "Data Scientist",
            "company": "Royal Dutch Shell",
            "period": "Sep 2016 – May 2022",
            "type": "past",
            "logo": "🟡",
            "highlights": [
                "Built Power BI forecasting dashboard for materials on-time delivery across 5 geographies, saving 10% budget",
                "Developed predictive maintenance ML models (XGBoost, Random Forest) — 30% cost reduction, 25% less downtime",
                "5+ years with databases, data warehousing, ETL and big data analytics technologies",
                "Applied classification, clustering, statistical inference with scikit-learn, TensorFlow, Keras, PyTorch",
            ],
            "tags": ["XGBoost", "Python", "Power BI", "PySpark", "TensorFlow", "PyTorch", "ETL"],
        },
        {
            "role": "IT Analyst",
            "company": "Tata Consultancy Services (TCS)",
            "period": "Dec 2010 – Aug 2016",
            "type": "past",
            "logo": "🟣",
            "highlights": [
                "Performed System Integration Testing & UAT to validate client PoS systems",
                "Led offshore teams in the UK for implementation of new PoS software",
                "Worked with card and payment systems, PCI standards and ISO 8583 protocols",
            ],
            "tags": ["System Testing", "UAT", "PCI Standards", "ISO 8583", "PoS Systems"],
        },
    ]

    EDUCATION = [
        {
            "degree": "M.S. in Machine Learning & Artificial Intelligence",
            "school": "Liverpool John Moores University",
            "period": "2023 – 2025",
            "note": "Research thesis on integrating LLMs (GPT-3.5, Mixtral, Llama 3.1) with classical ML models",
        },
        {
            "degree": "Executive PG in Data Science & AI",
            "school": "IIIT Bangalore",
            "period": "2022 – 2023",
            "note": "Statistics, Python, ML, NLP, Neural Networks, MLOps",
        },
        {
            "degree": "B.E. in Electronics & Communication",
            "school": "New Horizon College of Engineering, VTU",
            "period": "2006 – 2010",
            "note": "",
        },
    ]

    # ── Timeline ──
    for i, job in enumerate(EXPERIENCE):
        is_current = job["type"] == "current"
        border_color = accent if is_current else (tag_border if not dark else "#333")
        dot_bg = accent if is_current else text_muted

        # Build tag chips
        job_chips = "".join(
            f'<span style="background:{tag_bg};color:{text_muted};font-size:11px;font-family:JetBrains Mono,monospace;padding:3px 9px;border-radius:4px;margin-right:5px;margin-bottom:4px;display:inline-block;">{t}</span>'
            for t in job["tags"]
        )

        # Build bullet points
        bullets = "".join(
            f'<li style="font-size:15px;color:{text_body};font-family:Comic Sans MS,cursive;line-height:1.7;margin-bottom:6px;">{h}</li>'
            for h in job["highlights"]
        )

        # Current badge
        badge = f'<span style="background:{accent};color:#fff;font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;font-family:Comic Sans MS,cursive;margin-left:10px;">● Current</span>' if is_current else ""

        # Connector line between timeline dots
        connector = f'<div style="width:2px;flex:1;background:{hr_color};margin-top:8px;"></div>' if i < len(EXPERIENCE) - 1 else ""

        st.markdown(
            f'<div style="display:flex;gap:20px;margin-bottom:32px;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;min-width:40px;">'
            f'<div style="width:40px;height:40px;border-radius:50%;background:{dot_bg};display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">{job["logo"]}</div>'
            f'{connector}'
            f'</div>'
            f'<div style="flex:1;background:{card_bg};border:1px solid {border_color};border-radius:14px;padding:22px 26px;margin-bottom:8px;">'
            f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:6px;">'
            f'<span style="font-family:Comic Sans MS,cursive;font-size:19px;font-weight:700;color:{text_main};">{job["role"]}</span>'
            f'{badge}'
            f'</div>'
            f'<div style="font-size:15px;color:{accent};font-weight:600;font-family:Comic Sans MS,cursive;margin-bottom:4px;">{job["company"]}</div>'
            f'<div style="font-size:13px;color:{text_muted};font-family:JetBrains Mono,monospace;margin-bottom:16px;">📅 {job["period"]}</div>'
            f'<ul style="margin:0 0 16px 0;padding-left:20px;">{bullets}</ul>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;">{job_chips}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Education ──
    st.markdown(f'<div style="font-size:12px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;font-weight:700;margin:16px 0 20px 0;font-family:Comic Sans MS,cursive;">🎓 Education</div>', unsafe_allow_html=True)

    for edu in EDUCATION:
        note_html = f'<div style="font-size:13px;color:{text_muted};font-family:Comic Sans MS,cursive;">{edu["note"]}</div>' if edu["note"] else ""
        st.markdown(
            f'<div style="background:{card_bg};border:1px solid {card_border};border-left:3px solid {accent};border-radius:10px;padding:16px 20px;margin-bottom:12px;">'
            f'<div style="font-size:16px;font-weight:700;color:{text_main};font-family:Comic Sans MS,cursive;margin-bottom:4px;">{edu["degree"]}</div>'
            f'<div style="font-size:14px;color:{accent};font-weight:600;font-family:Comic Sans MS,cursive;margin-bottom:4px;">{edu["school"]}</div>'
            f'<div style="font-size:12px;color:{text_muted};font-family:JetBrains Mono,monospace;margin-bottom:{"6px" if edu["note"] else "0"};">📅 {edu["period"]}</div>'
            f'{note_html}'
            f'</div>',
            unsafe_allow_html=True
        )


# ── TAB 3: RESUME ──────────────────────────────────────────────────────────────
with resume_tab:
    if os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            pdf_bytes = f.read()

        b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        st.download_button(
            label="⬇️  Download Resume",
            data=pdf_bytes,
            file_name="Hargurjeet_Lead_GenAI_Specialist.pdf",
            mime="application/pdf"
        )

        import streamlit.components.v1 as components
        components.html(f"""
            <script>
                const b64 = "{b64}";
                const binary = atob(b64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) {{
                    bytes[i] = binary.charCodeAt(i);
                }}
                const blob = new Blob([bytes], {{type: 'application/pdf'}});
                const url = URL.createObjectURL(blob);
                const iframe = document.createElement('iframe');
                iframe.src = url;
                iframe.width = '100%';
                iframe.height = '860px';
                iframe.style.border = 'none';
                iframe.style.borderRadius = '12px';
                document.body.appendChild(iframe);
            </script>
        """, height=880)
    else:
        st.error(f"⚠️ Resume not found at `{RESUME_PATH}`.")


# ── TAB 3: BLOGS ───────────────────────────────────────────────────────────────
with blogs_tab:

    BLOGS = [
        {"title": "Stop Writing Buggy APIs: Why Pydantic Should Be Your New Best Friend", "platform": "LinkedIn", "url": "https://www.linkedin.com/pulse/stop-writing-buggy-apis-why-pydantic-should-your-new-best-ganger-vpcpc/?trackingId=lzRLeNiCTYaVpRzDr6fB0A%3D%3D", "emoji": "🔗"},
        {"title": "From Videos to Blogs: Unlock Content Creation with Crewai", "platform": "Medium", "url": "https://gurjeet333.medium.com/from-videos-to-blogs-unlock-content-creation-with-crewai-774f1bc083bf", "emoji": "🎬"},
        {"title": "Mastering AI Agents: A Journey from Basics to Execution", "platform": "Medium", "url": "https://gurjeet333.medium.com/mastering-ai-agents-a-journey-from-basics-to-execution-3ec35c6aa93c", "emoji": "🧠"},
        {"title": "Time Series Forecasting Using AUTO ARIMA + PROPHET + LightGBM", "platform": "Medium", "url": "https://gurjeet333.medium.com/time-series-forecasting-using-auto-arima-prophet-lightgbm-6362ef486c95", "emoji": "📈"},
        {"title": "Machine Learning with Python: Implementing XGBoost and Random Forest", "platform": "Medium", "url": "https://gurjeet333.medium.com/machine-learning-with-python-implementing-xgboost-and-random-forest-fd51fa4f9f4c", "emoji": "🌲"},
        {"title": "Learn how to build an advanced chatbot with a cloud vector database", "platform": "Medium", "url": "https://gurjeet333.medium.com/learn-how-to-build-a-chatbot-from-scratch-on-a-free-cloud-vector-database-193a7fa29c13", "emoji": "💬"},
        {"title": "Performing Sentence Similarity By Leveraging Hugging Face APIs", "platform": "Medium", "url": "https://gurjeet333.medium.com/performing-sentence-similarity-by-leveraging-hugging-face-apis-8ca0846e299c", "emoji": "🤗"},
        {"title": "Working with SQL in Python Environment?", "platform": "Medium", "url": "https://gurjeet333.medium.com/working-with-sql-in-python-environment-917385774583", "emoji": "🗄️"},
        {"title": "Best Known Techniques For Data Scientist To Handle Missing/Null Values", "platform": "Medium", "url": "https://gurjeet333.medium.com/best-known-techniques-for-data-scientist-to-handle-missing-null-values-in-any-tabular-dataset-3a9f71c9486", "emoji": "🔧"},
        {"title": "Sentiment Analysis of Movie Reviews with Google's BERT", "platform": "Medium", "url": "https://gurjeet333.medium.com/sentiment-analysis-of-movie-reviews-with-googles-bert-c2b97f4217f", "emoji": "🎬"},
        {"title": "Understanding Machine Learning Pipeline — A Gentle Introduction", "platform": "Medium", "url": "https://gurjeet333.medium.com/understanding-machine-learning-pipeline-a-gentle-introduction-ca96419108dc", "emoji": "🔄"},
        {"title": "Learning k-folds Cross Validations", "platform": "Medium", "url": "https://gurjeet333.medium.com/learning-k-folds-cross-validations-69b981c91e3a", "emoji": "📐"},
        {"title": "Building Recommendations System? A Beginner Guide", "platform": "Medium", "url": "https://gurjeet333.medium.com/building-recommendations-system-a-beginner-guide-8593f205bc0a", "emoji": "⭐"},
        {"title": "What Should I Read Next? Books Recommendation", "platform": "Medium", "url": "https://medium.com/nerd-for-tech/what-should-i-read-next-books-recommendation-311666254817", "emoji": "📚"},
        {"title": "NLP — Detecting Fake News On Social Media", "platform": "Medium", "url": "https://gurjeet333.medium.com/nlp-detecting-fake-news-on-social-media-aa53ff74f2ff", "emoji": "📰"},
        {"title": "Fake or Not? Twitter Disaster Tweets", "platform": "Medium", "url": "https://medium.com/geekculture/fake-or-not-twitter-disaster-tweets-f1a6b2311be9", "emoji": "🐦"},
        {"title": "PyTorch — Training Fruit 360 Classifier Under 5 mins", "platform": "Medium", "url": "https://medium.com/geekculture/pytorch-training-fruit-360-classifier-under-5-mins-23153b46ec88", "emoji": "🍎"},
        {"title": "7 Best Techniques To Improve The Accuracy of CNN W/O Overfitting", "platform": "Medium", "url": "https://gurjeet333.medium.com/7-best-techniques-to-improve-the-accuracy-of-cnn-w-o-overfitting-6db06467182f", "emoji": "🎯"},
        {"title": "Training Convolutional Neural Network on GPU From Scratch", "platform": "Medium", "url": "https://gurjeet333.medium.com/training-convolutional-neural-network-convnet-cnn-on-gpu-from-scratch-439e9fdc13a5", "emoji": "⚡"},
        {"title": "Training Feed Forward Neural Network on GPU — Beginners Guide", "platform": "Medium", "url": "https://gurjeet333.medium.com/training-feed-forward-neural-network-ffnn-on-gpu-beginners-guide-2d04254deca9", "emoji": "🔬"},
        {"title": "Logistic Regression With PyTorch — A Beginner Guide", "platform": "Medium", "url": "https://medium.com/analytics-vidhya/logistic-regression-with-pytorch-a-beginner-guide-33c2266ad129", "emoji": "📊"},
        {"title": "Getting Started With Machine Learning — Swedish Auto Insurance Dataset", "platform": "Medium", "url": "https://gurjeet333.medium.com/getting-started-with-machine-learning-swedish-auto-insurance-dataset-e3583267d0ee", "emoji": "🚗"},
        {"title": "Explanatory Data Analysis With Python - Beginners Guide", "platform": "Medium", "url": "https://medium.com/geekculture/covid-19-explanatory-data-analysis-76cab46c48d1", "emoji": "🔍"},
        {"title": "Exploratory Data Analysis of Zomato's Restaurant Dataset", "platform": "Medium", "url": "https://gurjeet333.medium.com/explanatory-data-analysis-of-zomato-restaurant-data-71ba8c3c7e5e", "emoji": "🍽️"},
        {"title": "Deep Learning for Beginners Using TensorFlow", "platform": "Medium", "url": "https://medium.com/analytics-vidhya/cnn-german-traffic-signal-recognition-benchmarking-using-tensorflow-accuracy-80-d069b7996082", "emoji": "🤖"},
        {"title": "CNN Model for Gender and Ethnicity Prediction with Tensorflow", "platform": "Medium", "url": "https://gurjeet333.medium.com/cnn-model-for-gender-and-ethnicity-prediction-with-tensorflow-ffbbaa4efdad", "emoji": "👤"},
        {"title": "Data Exploration of historical Olympics dataset", "platform": "Medium", "url": "https://medium.com/nerd-for-tech/data-exploration-of-historical-olympics-dataset-2d50a7d0611d", "emoji": "🏅"},
    ]

    def platform_badge(platform):
        if platform == "LinkedIn":
            bg_b, txt, icon = "#1a3a5c", "#4da6ff", "in"
        else:
            bg_b, txt, icon = "#2a1a1a", "#ff6b4a", "M"
        return f'<span style="background:{bg_b};color:{txt};font-size:11px;font-weight:700;letter-spacing:0.5px;padding:4px 10px;border-radius:4px;font-family:JetBrains Mono,monospace;">{icon} {platform}</span>'

    featured = BLOGS[0]
    rest = BLOGS[1:]

    st.markdown(f'<div style="font-size:12px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;font-weight:700;margin-bottom:16px;margin-top:8px;font-family:Comic Sans MS,cursive;">⭐ Featured</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{featured['url']}" target="_blank" style="text-decoration:none;">
        <div style="background:{card_bg};border:1px solid {card_border};border-radius:18px;padding:34px 40px;display:flex;align-items:center;gap:32px;margin-bottom:28px;cursor:pointer;transition:border-color 0.2s;" onmouseover="this.style.borderColor='{accent}'" onmouseout="this.style.borderColor='{card_border}'">
            <div style="font-size:52px;min-width:80px;height:80px;background:{tag_bg};border-radius:14px;display:flex;align-items:center;justify-content:center;">{featured['emoji']}</div>
            <div style="flex:1;">
                <div style="margin-bottom:12px;">{platform_badge(featured['platform'])}</div>
                <div style="font-family:Comic Sans MS,cursive;font-size:22px;color:{text_main};line-height:1.4;margin-bottom:12px;font-weight:700;">{featured['title']}</div>
                <div style="font-size:14px;color:{accent};font-weight:600;font-family:Comic Sans MS,cursive;">Read article →</div>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:12px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;font-weight:700;margin-bottom:16px;font-family:Comic Sans MS,cursive;">📝 All Posts</div>', unsafe_allow_html=True)

    for blog in rest:
        a = "#4da6ff" if blog["platform"] == "LinkedIn" else accent
        st.markdown(f"""
        <a href="{blog['url']}" target="_blank" style="text-decoration:none;">
            <div style="background:{blog_bg};border:1px solid {blog_bdr};border-left:3px solid {a};border-radius:10px;padding:18px 22px;display:flex;align-items:center;gap:16px;margin-bottom:9px;transition:background 0.2s;" onmouseover="this.style.background='{hover_bg}'" onmouseout="this.style.background='{blog_bg}'">
                <div style="font-size:24px;min-width:36px;text-align:center;">{blog['emoji']}</div>
                <div style="flex:1;font-size:15px;color:{text_body};font-weight:600;line-height:1.5;font-family:Comic Sans MS,cursive;">{blog['title']}</div>
                <div>{platform_badge(blog['platform'])}</div>
                <div style="color:{text_muted};font-size:18px;padding-left:8px;">→</div>
            </div>
        </a>
        """, unsafe_allow_html=True)


# ── TAB 4: PROJECTS ────────────────────────────────────────────────────────────
with projects_tab:

    PROJECTS = [
        {
            "title": "Finance Planner",
            "description": "An AI-powered retirement planning tool built with CrewAI and AWS Bedrock.",
            "banner": "https://plus.unsplash.com/premium_photo-1723802573606-f3828a8975c8?w=1200&q=80",
            "tags": ["Crewai", "FastAPI", "Streamlit", "Multi Agent Orchestration", "GPT-4o-mini", "Tool Calling"],
            "github_url": "https://github.com/hargurjeet/Finance_Planner",
            "live_url": "https://yourapp.streamlit.app",
            "status": "Live",
        },
        {
            "title": "Resume Parser",
            "description": "An intelligent resume parsing system powered by AWS Bedrock Claude and structured output validation. Extract structured candidate information from PDF resumes with high accuracy using AI.",
            "banner": "https://images.unsplash.com/photo-1698047681432-006d2449c631?w=1200&q=80",
            "tags": ["Python", "OpenAI", "Pandas", "AWS"],
            "github_url": "https://github.com/hargurjeet/resume-parser",
            "live_url": "https://huggingface.co/spaces/Hargurjeet/Resume_parser",
            "status": "Live",
        },
    ]

    st.markdown(f'<div style="font-size:12px;color:{text_dim};letter-spacing:1.5px;text-transform:uppercase;font-weight:700;margin-bottom:24px;margin-top:8px;font-family:Comic Sans MS,cursive;">🚀 Deployed Projects</div>', unsafe_allow_html=True)

    for project in PROJECTS:
        status_color = "#22c55e" if project["status"] == "Live" else "#f59e0b"
        tags_html = "".join([
            f'<span style="background:{tag_bg};color:{tag_color};font-size:12px;font-family:JetBrains Mono,monospace;padding:4px 12px;border-radius:4px;margin-right:6px;margin-bottom:4px;display:inline-block;">{tag}</span>'
            for tag in project["tags"]
        ])
        card = (
            f'<div style="background:{project_bg};border:1px solid {card_border};border-radius:18px;overflow:hidden;margin-bottom:28px;">'
                f'<div style="width:100%;height:185px;background-image:url({project["banner"]});background-size:cover;background-position:center;position:relative;">'
                    f'<div style="position:absolute;top:14px;right:14px;background:rgba(0,0,0,0.8);border:1px solid {status_color};color:{status_color};font-size:12px;font-weight:700;padding:5px 12px;border-radius:20px;font-family:Comic Sans MS,cursive;">&#9679; {project["status"]}</div>'
                '</div>'
                f'<div style="padding:26px 30px 24px 30px;">'
                    f'<div style="font-family:Comic Sans MS,cursive;font-size:22px;color:{text_main};margin-bottom:12px;line-height:1.3;font-weight:700;">{project["title"]}</div>'
                    f'<div style="font-size:15px;color:{text_muted};line-height:1.75;margin-bottom:18px;font-family:Comic Sans MS,cursive;">{project["description"]}</div>'
                    f'<div style="margin-bottom:22px;">{tags_html}</div>'
                    '<div style="display:flex;gap:12px;">'
                        f'<a href="{project["live_url"]}" target="_blank" style="text-decoration:none;"><div style="background:{accent};color:#fff;font-size:14px;font-weight:700;padding:10px 22px;border-radius:9px;display:inline-flex;align-items:center;gap:8px;font-family:Comic Sans MS,cursive;">🚀 Launch App</div></a>'
                        f'<a href="{project["github_url"]}" target="_blank" style="text-decoration:none;"><div style="background:transparent;color:{text_muted};border:1px solid {card_border};font-size:14px;font-weight:600;padding:10px 22px;border-radius:9px;display:inline-flex;align-items:center;gap:8px;font-family:Comic Sans MS,cursive;">🐙 View on GitHub</div></a>'
                    '</div>'
                '</div>'
            '</div>'
        )
        st.markdown(card, unsafe_allow_html=True)