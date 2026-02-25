import streamlit as st
import requests
import base64
import json
import os

import os
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/chat")
RESUME_PATH = "data/Hargurjeet_Lead_GenAI_Specialist.pdf"

st.set_page_config(
    page_title="Hargurjeet · AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force sidebar open on every rerun
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #0f0f0f;
    color: #e8e8e8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #141414;
    border-right: 1px solid #222;
}

[data-testid="stSidebar"] * {
    color: #e8e8e8 !important;
}

/* ── Hide default header & white ribbon ── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden !important;
}
[data-testid="stToolbar"] { display: none !important; }
.stDeployButton { display: none !important; }

/* ── Force sidebar open and visible ── */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    min-width: 260px !important;
    max-width: 260px !important;
    transform: none !important;
}

/* ── Hide the sidebar collapse arrow button ── */
[data-testid="collapsedControl"] {
    display: none !important;
}

button[kind="header"] {
    display: none !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1a1a1a;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #2a2a2a;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #888 !important;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 20px;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #ff5733 !important;
    color: #fff !important;
}

/* ── Chat container ── */
[data-testid="stVerticalBlock"] > div:has(.stContainer) > div {
    border-radius: 16px;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background-color: #1a1a1a !important;
    border: 1px solid #252525;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 8px;
}

[data-testid="stChatMessage"] p {
    font-size: 15px;
    line-height: 1.7;
    color: #e0e0e0;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 14px !important;
    color: #e8e8e8 !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #ff5733 !important;
    box-shadow: 0 0 0 2px rgba(255, 87, 51, 0.15) !important;
}

/* ── Expander (Sources) ── */
[data-testid="stExpander"] {
    background-color: #161616 !important;
    border: 1px solid #252525 !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary {
    font-size: 13px !important;
    color: #888 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Suggestion buttons ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background-color: #1a1a1a !important;
    color: #888 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 20px !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    font-weight: 400 !important;
    transition: all 0.2s ease;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background-color: #222 !important;
    color: #ff5733 !important;
    border-color: #ff5733 !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: transparent;
    color: #ff5733 !important;
    border: 1px solid #ff5733 !important;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 13px;
    padding: 6px 16px;
    transition: all 0.2s ease;
    width: 100%;
}

.stButton > button:hover {
    background-color: #ff5733 !important;
    color: #fff !important;
}

.stDownloadButton > button {
    background-color: #ff5733 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    width: 100%;
    padding: 10px;
}

/* ── Divider ── */
hr {
    border-color: #222 !important;
    margin: 16px 0;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f0f0f; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #ff5733; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #ff5733 !important; }

/* ── Caption / small text ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #555 !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Profile header
    st.markdown("""
    <div style="text-align: center; padding: 24px 0 16px 0;">
        <div style="
            width: 72px; height: 72px;
            background: linear-gradient(135deg, #ff5733, #ff8c42);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 28px;
            margin: 0 auto 14px auto;
            box-shadow: 0 4px 20px rgba(255,87,51,0.3);
        ">H</div>
        <div style="font-family: 'DM Serif Display', serif; font-size: 20px; color: #f0f0f0; margin-bottom: 4px;">
            Hargurjeet Singh
        </div>
        <div style="font-size: 12px; color: #ff5733; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase;">
            Lead GenAI Specialist
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Quick links
    st.markdown("""
    <div style="padding: 0 4px;">
        <div style="font-size: 11px; color: #555; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px; font-weight: 600;">Connect</div>
        <a href="https://linkedin.com" target="_blank" style="
            display: flex; align-items: center; gap: 10px;
            color: #aaa; text-decoration: none; font-size: 14px;
            padding: 8px 10px; border-radius: 8px;
            transition: background 0.2s;
            margin-bottom: 4px;
        " onmouseover="this.style.background='#222'" onmouseout="this.style.background='transparent'">
            🔗 &nbsp;LinkedIn
        </a>
        <a href="https://github.com" target="_blank" style="
            display: flex; align-items: center; gap: 10px;
            color: #aaa; text-decoration: none; font-size: 14px;
            padding: 8px 10px; border-radius: 8px;
            margin-bottom: 4px;
        " onmouseover="this.style.background='#222'" onmouseout="this.style.background='transparent'">
            🐙 &nbsp;GitHub
        </a>
        <a href="mailto:hargurjeet@example.com" style="
            display: flex; align-items: center; gap: 10px;
            color: #aaa; text-decoration: none; font-size: 14px;
            padding: 8px 10px; border-radius: 8px;
        " onmouseover="this.style.background='#222'" onmouseout="this.style.background='transparent'">
            ✉️ &nbsp;Email
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Stats
    st.markdown("""
    <div style="padding: 0 4px;">
        <div style="font-size: 11px; color: #555; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px; font-weight: 600;">Quick Facts</div>
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px;">
                <span style="color: #777;">Experience</span>
                <span style="color: #ff5733; font-weight: 600;">15+ years</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 13px;">
                <span style="color: #777;">Speciality</span>
                <span style="color: #ff5733; font-weight: 600;">GenAI / ML</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 13px;">
                <span style="color: #777;">Cloud</span>
                <span style="color: #ff5733; font-weight: 600;">AWS · GCP</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Clear chat button
    if st.button("🗑️  Clear Conversation"):
        st.session_state.messages = []
        st.session_state.sources = {}
        st.rerun()

    st.markdown("""
    <div style="text-align: center; margin-top: 16px; font-size: 11px; color: #333;">
        Powered by GPT-4o-mini · LangChain · FAISS
    </div>
    """, unsafe_allow_html=True)


# ── PAGE HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 32px 0 20px 0;">
    <div style="font-family: 'DM Serif Display', serif; font-size: 36px; color: #f0f0f0; line-height: 1.1;">
        Ask me anything
    </div>
    <div style="font-size: 15px; color: #555; margin-top: 6px;">
        about Hargurjeet's experience, skills, and background
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
chat_tab, resume_tab, blogs_tab, projects_tab = st.tabs(["💬  Chat", "📄  Resume", "✍️  Blogs", "🚀  Projects"])


# ── TAB 1: CHAT ────────────────────────────────────────────────────────────────
with chat_tab:

    # Initialise session state
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

    # Scrollable chat container
    chat_container = st.container(height=520)
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="
                display: flex; flex-direction: column;
                align-items: center; justify-content: center;
                height: 280px; gap: 12px;
            ">
                <div style="font-size: 40px;">⚡</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 22px; color: #444;">
                    Start a conversation
                </div>
                <div style="font-size: 13px; color: #333; text-align: center; max-width: 320px; line-height: 1.6;">
                    Click a suggestion below or type your own question
                </div>
            </div>
            """, unsafe_allow_html=True)

        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and i in st.session_state.sources:
                    with st.expander("📎 Sources"):
                        for j, src in enumerate(st.session_state.sources[i]):
                            st.markdown(f"`[{j+1}]` {src['source']} — page {src['page']}")

    # ── Suggestion buttons (only shown when no messages yet) ──
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

    # ── Chat input — also handles preset questions from suggestion buttons ──
    user_input = st.chat_input("Ask anything about Hargurjeet...")

    # Pick up either typed input or button-triggered preset
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

                with chat_container:
                    with st.chat_message("assistant"):
                        token_placeholder = st.empty()

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
                                full_answer += data["token"]
                                token_placeholder.markdown(full_answer + "▌")

                            if "sources" in data:
                                sources = data["sources"]

                        token_placeholder.markdown(full_answer)

                        if sources:
                            with st.expander("📎 Sources"):
                                for j, src in enumerate(sources):
                                    st.markdown(f"`[{j+1}]` {src['source']} — page {src['page']}")

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


# ── TAB 2: RESUME ──────────────────────────────────────────────────────────────
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

    # ── Blog data — update this list with your real posts ──
    BLOGS = [
        {
            "title": "Building a Production-Ready RAG Pipeline with LangChain and FAISS",
            "platform": "Medium",
            "url": "https://medium.com",
            "thumbnail": "https://miro.medium.com/v2/resize:fit:1200/1*placeholder.png",
            "emoji": "🔗",
        },
        {
            "title": "From Zero to GenAI: How I Built an LLM Evaluation Framework",
            "platform": "Medium",
            "url": "https://medium.com",
            "thumbnail": "",
            "emoji": "🧠",
        },
        {
            "title": "Why Agentic AI is the Next Frontier for Enterprise Automation",
            "platform": "LinkedIn",
            "url": "https://linkedin.com",
            "thumbnail": "",
            "emoji": "🤖",
        },
        {
            "title": "Lessons from Deploying ML Models on AWS at Scale",
            "platform": "Medium",
            "url": "https://medium.com",
            "thumbnail": "",
            "emoji": "☁️",
        },
        {
            "title": "XGBoost vs Random Forest: Which One for Your Use Case?",
            "platform": "LinkedIn",
            "url": "https://linkedin.com",
            "thumbnail": "",
            "emoji": "📊",
        },
    ]

    PLATFORM_COLORS = {
        "Medium":   {"bg": "#1a1a1a", "badge": "#292929", "text": "#e8e8e8", "accent": "#ff5733"},
        "LinkedIn": {"bg": "#1a1a1a", "badge": "#1a3a5c", "text": "#e8e8e8", "accent": "#0a66c2"},
    }

    def platform_badge(platform):
        color = PLATFORM_COLORS.get(platform, {}).get("badge", "#333")
        text_color = "#0a66c2" if platform == "LinkedIn" else "#ff5733"
        icon = "in" if platform == "LinkedIn" else "M"
        return f"""
        <span style="
            background:{color}; color:{text_color};
            font-size:11px; font-weight:700; letter-spacing:0.5px;
            padding:3px 9px; border-radius:4px;
            font-family:'JetBrains Mono', monospace;
        ">{icon} {platform}</span>"""

    featured = BLOGS[0]
    rest = BLOGS[1:]

    # ── FEATURED BLOG ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:11px; color:#555; letter-spacing:1.5px;
         text-transform:uppercase; font-weight:600; margin-bottom:14px; margin-top:8px;">
        Featured
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a href="{featured['url']}" target="_blank" style="text-decoration:none;">
        <div style="
            background: linear-gradient(135deg, #1a1a1a 0%, #1f1f1f 100%);
            border: 1px solid #2a2a2a;
            border-radius: 16px;
            padding: 32px 36px;
            display: flex; align-items: center; gap: 32px;
            transition: border-color 0.2s;
            margin-bottom: 28px;
            cursor: pointer;
        " onmouseover="this.style.borderColor='#ff5733'" onmouseout="this.style.borderColor='#2a2a2a'">
            <div style="
                font-size: 52px; min-width: 80px; height: 80px;
                background: #252525; border-radius: 14px;
                display: flex; align-items: center; justify-content: center;
            ">{featured['emoji']}</div>
            <div style="flex: 1;">
                <div style="margin-bottom: 10px;">{platform_badge(featured['platform'])}</div>
                <div style="
                    font-family: 'DM Serif Display', serif;
                    font-size: 22px; color: #f0f0f0; line-height: 1.35;
                    margin-bottom: 10px;
                ">{featured['title']}</div>
                <div style="font-size: 13px; color: #ff5733; font-weight: 500;">
                    Read article →
                </div>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

    # ── REST OF BLOGS ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:11px; color:#555; letter-spacing:1.5px;
         text-transform:uppercase; font-weight:600; margin-bottom:14px;">
        All Posts
    </div>
    """, unsafe_allow_html=True)

    for blog in rest:
        accent = "#0a66c2" if blog["platform"] == "LinkedIn" else "#ff5733"
        st.markdown(f"""
        <a href="{blog['url']}" target="_blank" style="text-decoration:none;">
            <div style="
                background: #141414;
                border: 1px solid #222;
                border-left: 3px solid {accent};
                border-radius: 10px;
                padding: 18px 22px;
                display: flex; align-items: center; gap: 18px;
                margin-bottom: 10px;
                transition: background 0.2s;
            " onmouseover="this.style.background='#1a1a1a'" onmouseout="this.style.background='#141414'">
                <div style="font-size:26px; min-width:40px; text-align:center;">{blog['emoji']}</div>
                <div style="flex:1;">
                    <div style="font-size:15px; color:#e0e0e0; font-weight:500; line-height:1.4;">
                        {blog['title']}
                    </div>
                </div>
                <div>{platform_badge(blog['platform'])}</div>
                <div style="color:#444; font-size:18px; padding-left:8px;">→</div>
            </div>
        </a>
        """, unsafe_allow_html=True)


# ── TAB 4: PROJECTS ────────────────────────────────────────────────────────────
with projects_tab:

    PROJECTS = [
        {
            "title": "Portfolio AI Chatbot",
            "description": "A production-ready RAG-powered chatbot built with LangChain, FAISS, FastAPI and Streamlit. Answers questions about my experience using GPT-4o-mini with conversational memory and streaming responses.",
            "banner": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&q=80",
            "tags": ["LangChain", "FastAPI", "Streamlit", "FAISS", "GPT-4o-mini"],
            "github_url": "https://github.com",
            "live_url": "https://yourapp.streamlit.app",
            "status": "Live",
        },
        {
            "title": "LLM Evaluation Framework",
            "description": "An end-to-end framework for evaluating large language model outputs across accuracy, hallucination rate, and latency. Designed for enterprise GenAI deployments.",
            "banner": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80",
            "tags": ["Python", "OpenAI", "Pandas", "AWS"],
            "github_url": "https://github.com",
            "live_url": "https://yourapp.streamlit.app",
            "status": "Live",
        },
        {
            "title": "ML Recommendation Engine",
            "description": "A multi-label recommendation system using Random Forest and XGBoost that increased premium product sales by 10%. Built for scale on GCP with real-time inference.",
            "banner": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
            "tags": ["XGBoost", "Scikit-learn", "GCP", "Docker"],
            "github_url": "https://github.com",
            "live_url": "https://yourapp.streamlit.app",
            "status": "Live",
        },
    ]

    st.markdown(
        '<div style="font-size:11px;color:#555;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;margin-bottom:20px;margin-top:8px;">Deployed Projects</div>',
        unsafe_allow_html=True
    )

    for project in PROJECTS:
        status_color = "#22c55e" if project["status"] == "Live" else "#f59e0b"

        tags_html = "".join([
            f'<span style="background:#252525;color:#888;font-size:11px;font-family:JetBrains Mono,monospace;padding:3px 10px;border-radius:4px;margin-right:6px;margin-bottom:4px;display:inline-block;">{tag}</span>'
            for tag in project["tags"]
        ])

        card = (
            '<div style="background:#141414;border:1px solid #222;border-radius:16px;overflow:hidden;margin-bottom:24px;">'
                f'<div style="width:100%;height:180px;background-image:url({project["banner"]});background-size:cover;background-position:center;position:relative;">'
                    f'<div style="position:absolute;top:14px;right:14px;background:rgba(0,0,0,0.75);border:1px solid {status_color};color:{status_color};font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;letter-spacing:0.5px;">&#9679; {project["status"]}</div>'
                '</div>'
                '<div style="padding:22px 26px 20px 26px;">'
                    f'<div style="font-family:Georgia,serif;font-size:20px;color:#f0f0f0;margin-bottom:10px;line-height:1.3;">{project["title"]}</div>'
                    f'<div style="font-size:14px;color:#777;line-height:1.65;margin-bottom:16px;">{project["description"]}</div>'
                    f'<div style="margin-bottom:20px;">{tags_html}</div>'
                    '<div style="display:flex;gap:12px;">'
                        f'<a href="{project["live_url"]}" target="_blank" style="text-decoration:none;"><div style="background:#ff5733;color:#fff;font-size:13px;font-weight:600;padding:9px 20px;border-radius:8px;display:inline-flex;align-items:center;gap:7px;">🚀 Launch App</div></a>'
                        f'<a href="{project["github_url"]}" target="_blank" style="text-decoration:none;"><div style="background:transparent;color:#aaa;border:1px solid #333;font-size:13px;font-weight:500;padding:9px 20px;border-radius:8px;display:inline-flex;align-items:center;gap:7px;">🐙 View on GitHub</div></a>'
                    '</div>'
                '</div>'
            '</div>'
        )
        st.markdown(card, unsafe_allow_html=True)