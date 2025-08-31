"""
Filter components for dashboard
"""

import streamlit as st
from datetime import datetime

def create_year_filter(available_years, key="year_filter", default_all=True):
    """Create year filter component"""
    if f"selected_years_{key}" not in st.session_state:
        st.session_state[f"selected_years_{key}"] = ["Semua Tahun"] if default_all else []
    
    st.markdown("**📅 Pilih Tahun:**")
    
    # Display selected chips
    if st.session_state[f"selected_years_{key}"]:
        chips_html = '<div class="year-selection-area">'
        for year in st.session_state[f"selected_years_{key}"]:
            chips_html += f'<span class="year-chip selected">{year} ✕</span>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="year-selection-area"><em style="color: #ccc;">Tidak ada tahun dipilih</em></div>', unsafe_allow_html=True)
    
    # Control buttons
    col1, col2 = st.columns(2)
    
    with col1:
        semua_tahun_selected = "Semua Tahun" in st.session_state[f"selected_years_{key}"]
        button_text = "✅ Semua Tahun" if semua_tahun_selected else "📋 Semua Tahun"
        if st.button(button_text, key=f"all_years_{key}", use_container_width=True):
            if not semua_tahun_selected:
                st.session_state[f"selected_years_{key}"] = ["Semua Tahun"]
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All", key=f"clear_all_{key}", use_container_width=True):
            st.session_state[f"selected_years_{key}"] = []
            st.rerun()
    
    # Individual year buttons
    st.markdown("**Tahun Individual:**")
    cols = st.columns(min(4, len(available_years)))
    
    for i, year in enumerate(available_years):
        col_idx = i % len(cols)
        with cols[col_idx]:
            is_selected = year in st.session_state[f"selected_years_{key}"]
            button_text = f"✅ {year}" if is_selected else f"📅 {year}"
            
            if st.button(button_text, key=f"year_{year}_{key}", use_container_width=True):
                current_selection = st.session_state[f"selected_years_{key}"].copy()
                
                if "Semua Tahun" in current_selection:
                    current_selection.remove("Semua Tahun")
                
                if year in current_selection:
                    current_selection.remove(year)
                else:
                    current_selection.append(year)
                
                if not current_selection:
                    current_selection = ["Semua Tahun"]
                
                st.session_state[f"selected_years_{key}"] = sorted(
                    current_selection, 
                    key=lambda x: x if x == "Semua Tahun" else int(x)
                )
                st.rerun()
    
    return st.session_state[f"selected_years_{key}"]

def create_multiselect_filter(options, label, key, default=None):
    """Create multiselect filter"""
    if default is None:
        default = options[:5] if len(options) > 5 else options
    
    return st.multiselect(
        label,
        options=options,
        default=default,
        key=key
    )

def create_selectbox_filter(options, label, key, index=0):
    """Create selectbox filter"""
    return st.selectbox(
        label,
        options=options,
        index=index,
        key=key
    )

def create_slider_filter(min_val, max_val, label, key, value=None):
    """Create slider filter"""
    if value is None:
        value = (min_val, max_val)
    
    return st.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=value,
        key=key
    )

def create_date_filter(label, key, default_date=None):
    """Create date filter"""
    if default_date is None:
        default_date = datetime.now().date()
    
    return st.date_input(
        label,
        value=default_date,
        key=key
    )

def create_checkbox_filter(label, key, value=False):
    """Create checkbox filter"""
    return st.checkbox(
        label,
        value=value,
        key=key
    )