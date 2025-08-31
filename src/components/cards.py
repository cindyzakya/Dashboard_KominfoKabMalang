"""
Card components for the dashboard
"""

import streamlit as st

def create_dashboard_card(title, icon, description, features, page_key):
    """Create dashboard selection card"""
    st.markdown(f"""
    <div class="dashboard-card">
        <div>
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-description">
                {description}
                <br><br>
                <strong>Fitur Utama:</strong><br>
                {"<br>".join([f"• {feature}" for feature in features])}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button(f"🚀 Buka {title}", key=page_key, use_container_width=True):
        page_mapping = {
            "kesehatan": "pages/dashboard_kesehatan.py",
            "sosial": "pages/dashboard_sosial.py", 
            "pendidikan": "pages/dashboard_pendidikan.py"
        }
        st.switch_page(page_mapping[page_key])

def create_kpi_card(title, value, icon, description=None):
    """Create KPI card component"""
    desc_html = f"<p>{description}</p>" if description else ""
    
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)
    
def create_white_kpi_card(value, title, description=None):
    """Create white KPI card component with optional description"""
    # Hanya tampilkan description jika ada dan tidak kosong
    desc_html = f'<div class="kpi-description">{description}</div>' if description and description.strip() else ""
    
    st.markdown(f"""
    <div class="white-kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-title">{title}</div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create metric card with optional delta"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_info_card(title, content, card_type="info"):
    """Create information card"""
    card_class = f"custom-alert custom-alert-{card_type}"
    
    st.markdown(f"""
    <div class="{card_class}">
        <strong>{title}:</strong> {content}
    </div>
    """, unsafe_allow_html=True)