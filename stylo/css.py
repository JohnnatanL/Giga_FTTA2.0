import streamlit as st


def aplicar_css_global():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --giga-bg: #071827;
        --giga-bg-2: #0b2b3d;
        --giga-card: rgba(255, 255, 255, 0.06);
        --giga-border: rgba(255, 255, 255, 0.14);
        --giga-text: #f8fafc;
        --giga-muted: #cbd5e1;
        --giga-blue: #00a7e1;
        --giga-green: #8cc63f;
        --giga-dark: #03111c;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(0,167,225,0.18), transparent 32%),
            linear-gradient(135deg, var(--giga-bg) 0%, var(--giga-bg-2) 100%);
        color: var(--giga-text);
    }



    </style>
    """, unsafe_allow_html=True)