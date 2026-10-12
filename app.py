import streamlit as st
import pandas as pd
import os
import io
import importlib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import backend

# Always reload backend to catch any live module changes
importlib.reload(backend)

# Page configuration
st.set_page_config(
    page_title="IWK Document Plan Dashboard",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Executive Slate Theme
st.markdown("""
<style>
    /* Google / Apple System Font Hierarchy & Smooth Rendering */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Main Canvas Background - Modern Soft Slate */
    .stApp {
        background-color: #f8fafc !important;
    }

    /* ======================================================== */
    /* EXECUTIVE DARK SIDEBAR STYLING                           */
    /* ======================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid #334155 !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #f8fafc !important;
    }
    
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: #94a3b8 !important;
    }
    
    section[data-testid="stSidebar"] hr {
        border-top: 1px solid rgba(255, 255, 255, 0.12) !important;
        margin: 16px 0 !important;
    }

    /* Sidebar Navigation Radio Buttons (Linear / Mac App Style) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        color: #cbd5e1 !important;
        transition: all 0.15s ease-in-out !important;
        cursor: pointer !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
        background: rgba(37, 99, 235, 0.35) !important;
        border: 1.5px solid #3b82f6 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.35) !important;
    }

    /* Sidebar Buttons */
    section[data-testid="stSidebar"] button {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(255, 255, 255, 0.16) !important;
        border-color: rgba(255, 255, 255, 0.35) !important;
        color: #ffffff !important;
    }

    /* Sidebar Code / Monospace */
    section[data-testid="stSidebar"] code {
        background: rgba(0, 0, 0, 0.3) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
    }

    /* ======================================================== */
    /* CARD CONTAINERS & FORMS (Modern Apple / Linear Elegance) */
    /* ======================================================== */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 8px 16px -2px rgba(15, 23, 42, 0.04) !important;
        padding: 18px 20px !important;
        margin-bottom: 18px !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 12px 24px -4px rgba(15, 23, 42, 0.06) !important;
    }

    /* Form Container */
    div[data-testid="stForm"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 22px 24px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 12px 24px -4px rgba(15, 23, 42, 0.05) !important;
    }

    /* Inputs & Selectboxes */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease-in-out !important;
    }

    div[data-baseweb="input"] > div:hover,
    div[data-baseweb="select"] > div:hover {
        border-color: #94a3b8 !important;
    }
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18) !important;
    }

    /* Input text color & weight */
    div[data-baseweb="input"] input {
        color: #0f172a !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    div[data-baseweb="select"] span {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
    }

    /* Widget Labels */
    label[data-testid="stWidgetLabel"] p {
        font-weight: 600 !important;
        color: #1e293b !important;
        font-size: 13.5px !important;
    }

    /* Buttons (Primary & Secondary) */
    button[data-testid="stBaseButton-primary"] {
        background: #2563eb !important;
        border-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3) !important;
    }
    button[data-testid="stBaseButton-secondary"] {
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        border-color: #94a3b8 !important;
        background: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 4px 12px rgba(15,23,42,0.03);
        border: 1px solid #e2e8f0;
        border-top: 3px solid #2563eb;
        margin-bottom: 12px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.05), 0 10px 20px rgba(15,23,42,0.05);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0;
        letter-spacing: -0.5px;
    }
    .metric-lbl {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    
    /* Modern Status Badges */
    .badge-complete {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-progress {
        background-color: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .badge-notstarted {
        background-color: #f8fafc;
        color: #475569;
        border: 1px solid #e2e8f0;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    
    /* Header decoration */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #334155 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: #94a3b8;
    }
    
    /* Clickable Project Title Button in timeline cards */
    button[data-testid="stBaseButton-tertiary"] {
        padding: 0px !important;
        margin: 0px !important;
        min-height: auto !important;
        height: auto !important;
        border: none !important;
        background: transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
    }
    button[data-testid="stBaseButton-tertiary"] p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin: 0 !important;
        line-height: 1.4 !important;
        cursor: pointer !important;
        transition: color 0.15s ease-in-out;
    }
    button[data-testid="stBaseButton-tertiary"]:hover p {
        color: #2563eb !important;
        text-decoration: underline !important;
    }

    /* Pills Alignment */
    div[data-testid="stPills"] {
        justify-content: flex-start !important;
    }
    div[data-testid="stPills"] button {
        border-radius: 9999px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }

    /* Dividers */
    hr {
        border-top: 1px solid #e2e8f0 !important;
        margin: 20px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'projects' not in st.session_state:
    st.session_state['projects'] = backend.load_document_plan()

if 'has_unsaved_changes' not in st.session_state:
    st.session_state['has_unsaved_changes'] = False

if 'sync_logs' not in st.session_state:
    st.session_state['sync_logs'] = []

if 'search_query_input' not in st.session_state:
    st.session_state['search_query_input'] = ""

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/microsoft-excel-2019--v1.png", width=64)
    st.title("Document Plan")
    st.caption("Excel Formula-driven Tracking System")
    st.divider()

    menu_options = [
        "📊 Dashboard & Metrics",
        "📋 Tracking Matrix (Checklists)",
        "🔄 Delivery Overview Sync",
        "💾 Save & Export Excel"
    ]
    if 'current_tab' not in st.session_state:
        st.session_state['current_tab'] = menu_options[0]

    if 'pending_tab' in st.session_state and st.session_state['pending_tab']:
        st.session_state['current_tab'] = st.session_state['pending_tab']
        del st.session_state['pending_tab']

    curr_idx = menu_options.index(st.session_state['current_tab']) if st.session_state['current_tab'] in menu_options else 0

    menu = st.radio(
        "Navigation",
        menu_options,
        index=curr_idx,
        key='radio_nav_' + str(st.session_state['current_tab'])
    )
    st.session_state['current_tab'] = menu
    st.divider()

    # Quick Status Card in Sidebar
    st.subheader("System Status")
    plan_file_exists = os.path.exists(backend.DEFAULT_DOCUMENT_PLAN)
    overview_file_exists = os.path.exists(backend.DEFAULT_DELIVERY_OVERVIEW)

    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
        <div style="font-size: 13px; color: #f8fafc; margin-bottom: 6px;">
            📁 <b>Master Plan:</b> {'<span style="color:#4ade80; font-weight:700;">● Connected</span>' if plan_file_exists else '<span style="color:#f87171; font-weight:700;">● Missing</span>'}
        </div>
        <div style="font-size: 11px; color: #94a3b8; font-family: monospace; word-break: break-all; margin-bottom: 10px;">
            {os.path.basename(backend.DEFAULT_DOCUMENT_PLAN)}
        </div>
        <div style="font-size: 13px; color: #f8fafc; margin-bottom: 6px;">
            🔄 <b>Delivery Overview:</b> {'<span style="color:#4ade80; font-weight:700;">● Connected</span>' if overview_file_exists else '<span style="color:#f87171; font-weight:700;">● Missing</span>'}
        </div>
        <div style="font-size: 11px; color: #94a3b8; font-family: monospace; word-break: break-all;">
            {os.path.basename(backend.DEFAULT_DELIVERY_OVERVIEW)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state['has_unsaved_changes']:
        st.warning("⚠️ Unsaved changes in App not yet written to Master Excel")
    else:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #6ee7b7; font-weight: 600; text-align: center; margin-bottom: 12px;">
            🟢 Synchronized with Master Excel
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 Reload Data from Excel", use_container_width=True):
        st.session_state['projects'] = backend.load_document_plan()
        st.session_state['has_unsaved_changes'] = False
        st.rerun()

# Header Banner
st.markdown("""
<div class="main-header">
    <h1>📑 IWK Document Plan & Quality Gate Dashboard</h1>
    <p>Real-time Excel Formula-driven Documentation Tracking System with Automated Delivery Overview Sync</p>
</div>
""", unsafe_allow_html=True)

projects = st.session_state['projects']

# Compute Overall KPIs
total_projects = len(projects)
complete_count = sum(1 for p in projects if p.get('calc_status') == 'Complete')
progress_count = sum(1 for p in projects if p.get('calc_status') == 'In Progress')
notstart_count = sum(1 for p in projects if p.get('calc_status') == 'Not Started')

total_docs_done = sum(p.get('calc_done', 0) for p in projects)
total_docs_req = sum(p.get('calc_req', 0) for p in projects)
overall_progress = (total_docs_done / total_docs_req * 100) if total_docs_req > 0 else 0.0

# KPI Display Rows
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f"""
    <div class="metric-card" style="border-top: 3px solid #2563eb;">
        <div class="metric-lbl">Total Projects</div>
        <div class="metric-val">{total_projects} <span style="font-size:15px; font-weight:500; color:#64748b;">Projects</span></div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card" style="border-top: 3px solid #10b981;">
        <div class="metric-lbl">Overall Progress</div>
        <div class="metric-val">{overall_progress:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card" style="border-top: 3px solid #f59e0b;">
        <div class="metric-lbl">Status Breakdown</div>
        <div class="metric-val" style="font-size: 16px; margin-top:8px;">
            <span class="badge-complete">Done: {complete_count}</span>
            <span class="badge-progress">WIP: {progress_count}</span>
            <span class="badge-notstarted">Wait: {notstart_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card" style="border-top: 3px solid #6366f1;">
        <div class="metric-lbl">Documents Ratio</div>
        <div class="metric-val">{total_docs_done} / {total_docs_req} <span style="font-size:14px; font-weight:500; color:#64748b;">Docs</span></div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 1: DASHBOARD & OVERVIEW
# ----------------------------------------------------
if menu == "📊 Dashboard & Metrics":
    st.subheader("📋 Projects Overview & Tracking")
    
    # Filter Row
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_query = st.text_input("🔍 Search by Project No. or Name", "", key="search_query_input")
    with f_col2:
        pm_list = ["All"] + sorted(list(set(str(p.get('pm', '')) for p in projects if p.get('pm'))))
        selected_pm = st.selectbox("Filter by PM", pm_list, key="filter_pm_select")
    with f_col3:
        status_options = ["All", "Complete", "In Progress", "Not Started"]
        selected_status = st.selectbox("Filter by Status", status_options, key="filter_status_select")

    # Filter data
    filtered = []
    for p in projects:
        p_no = str(p.get('project_no', ''))
        p_name = str(p.get('project_name', ''))
        pm = str(p.get('pm', ''))
        status = str(p.get('calc_status', ''))
        
        if search_query and (search_query.lower() not in p_no.lower() and search_query.lower() not in p_name.lower()):
            continue
        if selected_pm != "All" and pm != selected_pm:
            continue
        if selected_status != "All" and status != selected_status:
            continue
        filtered.append(p)

    # ----------------------------------------------------
    # VIEW TOGGLE BUTTONS (Hide / Unhide each view)
    # ----------------------------------------------------
    col_t_title, col_t_pills = st.columns([1, 4], vertical_alignment="center")
    with col_t_title:
        st.markdown("<span style='font-size:14px; font-weight:700; color:#1e293b;'>👁️ Toggle Views:</span>", unsafe_allow_html=True)
    with col_t_pills:
        view_modes = st.pills(
            "Toggle Views",
            options=[
                "📊 1. Resource Analytics",
                "📈 2. Visual Project Tracking",
                "📋 3. Clean Overview Table"
            ],
            default=[
                "📊 1. Resource Analytics",
                "📈 2. Visual Project Tracking",
                "📋 3. Clean Overview Table"
            ],
            selection_mode="multi",
            label_visibility="collapsed",
            key="overview_view_toggles",
            help="Click to Hide or Unhide each view independently"
        )

    if not view_modes:
        st.info("ℹ️ All views are hidden — click the buttons above to unhide views.")

    # ----------------------------------------------------
    # 1. RESOURCE ANALYTICS (Workload & Capacity)
    # ----------------------------------------------------
    if any("Resource Analytics" in str(v) or "1." in str(v) for v in (view_modes or [])):
        with st.container(border=True):
            r_top1, r_top2 = st.columns([2, 1], vertical_alignment="center")
            with r_top1:
                st.markdown("#### 📊 1. Resource Analytics & Workload Intelligence")
                st.caption("Analyze documentation workload distribution, capacity balance, and team collaboration opportunities")
            with r_top2:
                res_dim = st.radio(
                    "View Dimension:",
                    ["Document Owner (Who?)", "Project Manager (PM)"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

            # Aggregate data
            group_key = 'who' if res_dim == "Document Owner (Who?)" else 'pm'
            res_agg = {}
            total_req_all = 0
            total_done_all = 0
            for p in filtered:
                k = str(p.get(group_key) or ('Unassigned' if group_key == 'who' else 'Unassigned')).strip()
                if not k or k == '-':
                    k = 'Unassigned'
                req = p.get('calc_req', 0)
                done = p.get('calc_done', 0)
                pending = max(0, req - done)
                total_req_all += req
                total_done_all += done
                if k not in res_agg:
                    res_agg[k] = {'req': 0, 'done': 0, 'pending': 0, 'projs': 0, 'proj_list': []}
                res_agg[k]['req'] += req
                res_agg[k]['done'] += done
                res_agg[k]['pending'] += pending
                res_agg[k]['projs'] += 1
                res_agg[k]['proj_list'].append(str(p.get('project_no', '')))

            res_rows = []
            for k, val in res_agg.items():
                pct = (val['done'] / val['req'] * 100) if val['req'] > 0 else 0.0
                res_rows.append({
                    'name': k,
                    'req': val['req'],
                    'done': val['done'],
                    'pending': val['pending'],
                    'projs': val['projs'],
                    'pct': pct,
                    'proj_list': val['proj_list']
                })
            # Sort by total_req ascending for horizontal bar (largest at top)
            res_rows.sort(key=lambda x: (x['req'], x['done']))
            df_res = pd.DataFrame(res_rows)

            col_res_chart, col_res_insights = st.columns([1.2, 1], gap="medium")

            with col_res_chart:
                if not df_res.empty:
                    fig_res = go.Figure()
                    fig_res.add_trace(go.Bar(
                        y=df_res['name'],
                        x=df_res['done'],
                        name='Completed (Done)',
                        orientation='h',
                        marker=dict(color='#10b981'),
                        text=[f"{v} Docs" if v > 0 else "" for v in df_res['done']],
                        textposition='auto',
                        textfont=dict(color='#ffffff', size=11, family='Inter, sans-serif'),
                        hovertemplate='<b>%{y}</b><br>Completed: %{x} Docs<extra></extra>'
                    ))
                    fig_res.add_trace(go.Bar(
                        y=df_res['name'],
                        x=df_res['pending'],
                        name='In Progress (Pending)',
                        orientation='h',
                        marker=dict(color='#f97316'),
                        text=[f"{v} Docs" if v > 0 else "" for v in df_res['pending']],
                        textposition='auto',
                        textfont=dict(color='#ffffff', size=11, family='Inter, sans-serif'),
                        hovertemplate='<b>%{y}</b><br>Pending: %{x} Docs<extra></extra>'
                    ))
                    fig_res.update_layout(
                        barmode='stack',
                        height=max(260, len(df_res) * 45),
                        margin=dict(l=10, r=10, t=30, b=10),
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=1.02,
                            xanchor='right',
                            x=1,
                            font=dict(color='#1e293b', size=12, family='Inter, sans-serif')
                        ),
                        xaxis=dict(
                            title=dict(text='Documents (Units)', font=dict(color='#475569', size=12, family='Inter, sans-serif')),
                            gridcolor='#f1f5f9',
                            tickfont=dict(color='#64748b', family='Inter, sans-serif')
                        ),
                        yaxis=dict(
                            title='',
                            tickfont=dict(color='#0f172a', size=12, family='Inter, sans-serif')
                        ),
                        plot_bgcolor='#ffffff',
                        paper_bgcolor='#ffffff',
                        font=dict(family='Inter, sans-serif')
                    )
                    st.plotly_chart(fig_res, use_container_width=True)
                else:
                    st.info("No resource data matching the selected filter")

            with col_res_insights:
                dim_label = "Document Owner" if res_dim == "Document Owner (Who?)" else "Project Manager (PM)"
                
                # Build person options for dropdown
                all_names = [r['name'] for r in res_rows if r['name'] != 'Unassigned']
                all_names.sort()
                person_options = ["📌 All Team Overview"] + all_names
                if any(r['name'] == 'Unassigned' for r in res_rows):
                    person_options.append("Unassigned (Pending Allocation)")

                selected_person = st.selectbox(
                    f"👤 Select {dim_label} to Analyze:",
                    options=person_options,
                    index=0,
                    key=f"res_person_select_{group_key}",
                    help="Select an individual or all-team view to review workload, delivery progress, and support plans"
                )

                total_pending_all = max(0, total_req_all - total_done_all)
                overall_pct = (total_done_all / total_req_all * 100) if total_req_all > 0 else 0.0

                if selected_person == "📌 All Team Overview":
                    top_req_item = max(res_rows, key=lambda x: x['req']) if res_rows else None
                    free_capacity_items = [r for r in res_rows if r['name'] != 'Unassigned' and r['req'] > 0 and r['pending'] == 0]

                    st.markdown(f"""
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:10px 14px; border-radius:6px;">
                            <div style="font-weight:700; color:#1e40af; font-size:13px;">📦 1. Team Workload Distribution</div>
                            <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                Total <b>{total_req_all} required documents</b> across <b>{len(filtered)} projects</b> distributed among {len(all_names)} team members
                                {f'(Major share with <b>{top_req_item["name"]}</b>: {top_req_item["req"]} docs)' if top_req_item and top_req_item["name"] != "Unassigned" else ""}
                            </div>
                        </div>
                        <div style="background:#f0fdf4; border-left:4px solid #10b981; padding:10px 14px; border-radius:6px;">
                            <div style="font-weight:700; color:#065f46; font-size:13px;">🚀 2. Overall Delivery Progress</div>
                            <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                Delivered: <b>{total_done_all} documents ({overall_pct:.1f}%)</b> &nbsp;|&nbsp; In Progress: <b>{total_pending_all} documents</b>
                            </div>
                        </div>
                        <div style="background:#fffbeb; border-left:4px solid #f59e0b; padding:10px 14px; border-radius:6px;">
                            <div style="font-weight:700; color:#92400e; font-size:13px;">⚖️ 3. Capacity Balancing</div>
                            <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                {f"Some team members carry heavy workloads while <b>{free_capacity_items[0]['name']}</b> has achieved 100% completion (Available Capacity to assist team)" if free_capacity_items else "All team members are actively progressing according to milestone schedules"}
                            </div>
                        </div>
                        <div style="background:#f8fafc; border-left:4px solid #64748b; padding:10px 14px; border-radius:6px;">
                            <div style="font-weight:700; color:#334155; font-size:13px;">💡 4. Individual Deep-Dive</div>
                            <div style="font-size:13px; color:#475569; margin-top:2px;">
                                👆 Select a name from the dropdown above to view personalized workload analytics and support plans
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                elif selected_person == "Unassigned (Pending Allocation)":
                    unassigned_item = next((r for r in res_rows if r['name'] == 'Unassigned'), None)
                    p_projs = unassigned_item['projs'] if unassigned_item else 0
                    p_list = unassigned_item['proj_list'] if unassigned_item else []

                    st.markdown(f"""
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        <div style="background:#f8fafc; border-left:4px solid #64748b; padding:10px 14px; border-radius:6px;">
                            <div style="font-weight:700; color:#334155; font-size:13px;">📋 Projects with Unassigned {dim_label}</div>
                            <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                Total <b>{p_projs} projects</b>: <b>{', '.join(p_list)}</b>
                            </div>
                        </div>
                        <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:10px 14px; border-radius:6px;">
                            <div style="font-weight:700; color:#1e40af; font-size:13px;">💡 Allocation Recommendation</div>
                            <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                Recommend assigning document owners in advance to ensure documentation readiness before Quality Gate deadlines
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    # Individual Person Analysis
                    p_name = selected_person
                    p_item = next((r for r in res_rows if r['name'] == p_name), None)
                    if p_item:
                        p_req = p_item['req']
                        p_done = p_item['done']
                        p_pending = p_item['pending']
                        p_projs = p_item['projs']
                        p_pct = p_item['pct']
                        p_list = p_item['proj_list']
                        p_share = (p_req / total_req_all * 100) if total_req_all > 0 else 0.0

                        # Workload Intensity Level & Styling
                        if p_pending > 10:
                            intensity_badge = "🔴 High Workload"
                            intensity_bg = "#fef2f2"
                            intensity_border = "#ef4444"
                            intensity_color = "#991b1b"
                            intensity_desc = "Managing a high volume of documents across multiple projects. Primary contributor."
                            support_recommendation = "🤝 <b>Collaboration Recommendation:</b> As this member manages a major share of project documentation, consider delegating or rebalancing new project documents to team members with available capacity (e.g., pp) to ensure smooth milestones."
                        elif p_pending > 0:
                            intensity_badge = "🟡 Moderate Workload"
                            intensity_bg = "#fffbeb"
                            intensity_border = "#f59e0b"
                            intensity_color = "#92400e"
                            intensity_desc = "Managing project documents steadily according to plan."
                            support_recommendation = "🤝 <b>Collaboration Recommendation:</b> Workload is well-managed. Continue tracking per standard Quality Gate cadence."
                        elif p_req > 0 and p_pending == 0:
                            intensity_badge = "🟢 Full Completion (100% Delivered)"
                            intensity_bg = "#f0fdf4"
                            intensity_border = "#10b981"
                            intensity_color = "#065f46"
                            intensity_desc = "All assigned documents have been successfully completed."
                            support_recommendation = "✨ <b>Available Capacity:</b> High availability. Ready for new project assignments or assisting team members."
                        else:
                            intensity_badge = "⚪ Not Started / Unassigned"
                            intensity_bg = "#f8fafc"
                            intensity_border = "#94a3b8"
                            intensity_color = "#334155"
                            intensity_desc = "No required documents under current filter."
                            support_recommendation = "Ready for new document assignments."

                        st.markdown(f"""
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:10px 14px; border-radius:6px;">
                                <div style="font-weight:700; color:#1e40af; font-size:13px;">📋 1. Assigned Workload</div>
                                <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                    <b>{p_name}</b> manages <b>{p_req} documents</b> across <b>{p_projs} projects</b> ({', '.join(p_list)})
                                    <br><span style="font-size:12px; color:#64748b;">(Represents <b>{p_share:.1f}%</b> of total documentation portfolio in system)</span>
                                </div>
                            </div>
                            <div style="background:#f0fdf4; border-left:4px solid #10b981; padding:10px 14px; border-radius:6px;">
                                <div style="font-weight:700; color:#065f46; font-size:13px;">🚀 2. Delivery Progress</div>
                                <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                    Completed: <b>{p_done} documents</b> (<b>{p_pct:.1f}%</b> success rate)
                                    &nbsp;|&nbsp; In Progress: <b>{p_pending} documents</b>
                                </div>
                            </div>
                            <div style="background:{intensity_bg}; border-left:4px solid {intensity_border}; padding:10px 14px; border-radius:6px;">
                                <div style="font-weight:700; color:{intensity_color}; font-size:13px;">⚖️ 3. Workload Intensity</div>
                                <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                    <b>{intensity_badge}</b>
                                    <br><span style="font-size:12px; color:#475569;">{intensity_desc}</span>
                                </div>
                            </div>
                            <div style="background:#f8fafc; border-left:4px solid #6366f1; padding:10px 14px; border-radius:6px;">
                                <div style="font-weight:700; color:#4338ca; font-size:13px;">🤝 4. Collaboration & Support Plan</div>
                                <div style="font-size:13px; color:#1e293b; margin-top:2px;">
                                    {support_recommendation}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # 2. VISUAL PROJECT CHARTS (Progress & Status with Hide-Complete)
    # ----------------------------------------------------
    if any("Visual" in str(v) or "2." in str(v) for v in (view_modes or [])):
        with st.container(border=True):
            s2_top1, s2_top2 = st.columns([3, 1], vertical_alignment="center")
            with s2_top1:
                st.markdown("#### 📈 2. Visual Project Tracking & Progress")
                st.caption("Visual progress comparison across projects and overall completion status breakdown")
            with s2_top2:
                hide_comp_s2 = st.toggle("Hide Complete", value=False, key="toggle_hide_comp_s2", help="Exclude completed projects from visual tracking")

            filtered_s2 = [p for p in filtered if p.get('calc_status') != 'Complete'] if hide_comp_s2 else filtered

            c_pchart, c_pdonut = st.columns([1.5, 1], gap="medium")

            with c_pchart:
                proj_rows = []
                for p in filtered_s2:
                    p_name = str(p.get('project_name', ''))
                    if len(p_name) > 22:
                        p_name = p_name[:20] + '..'
                    p_label = f"{p.get('project_no')} - {p_name}"
                    req = p.get('calc_req', 0)
                    done = p.get('calc_done', 0)
                    pending = max(0, req - done)
                    pct = p.get('calc_progress', 0.0) * 100
                    proj_rows.append({
                        'label': p_label,
                        'project_no': p.get('project_no'),
                        'done': done,
                        'pending': pending,
                        'req': req,
                        'pct': pct,
                        'status': p.get('calc_status', 'Not Started'),
                        'pm': p.get('pm', '-'),
                        'who': p.get('who') or 'Unassigned'
                    })
                df_proj = pd.DataFrame(proj_rows).iloc[::-1]

                if not df_proj.empty:
                    fig_p = go.Figure()
                    fig_p.add_trace(go.Bar(
                        y=df_proj['label'],
                        x=df_proj['done'],
                        name='Completed (Docs Done)',
                        orientation='h',
                        marker=dict(color='#2563eb'),
                        text=df_proj.apply(lambda r: f"{r['pct']:.0f}% ({r['done']}/{r['req']})" if r['req'] > 0 else "0%", axis=1),
                        textposition='inside',
                        textfont=dict(color='#ffffff', size=11, family='Inter, sans-serif'),
                        hovertemplate='<b>%{y}</b><br>Completed: %{x} Docs<extra></extra>'
                    ))
                    fig_p.add_trace(go.Bar(
                        y=df_proj['label'],
                        x=df_proj['pending'],
                        name='Remaining (Pending)',
                        orientation='h',
                        marker=dict(color='#f1f5f9', line=dict(color='#cbd5e1', width=1)),
                        textposition='none',
                        hovertemplate='<b>%{y}</b><br>Remaining: %{x} Docs<extra></extra>'
                    ))
                    fig_p.update_layout(
                        barmode='stack',
                        height=max(320, len(df_proj) * 38),
                        margin=dict(l=10, r=10, t=30, b=10),
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=1.02,
                            xanchor='right',
                            x=1,
                            font=dict(color='#1e293b', size=12, family='Inter, sans-serif')
                        ),
                        xaxis=dict(
                            title=dict(text='Documents (Units)', font=dict(color='#475569', size=12, family='Inter, sans-serif')),
                            gridcolor='#f1f5f9',
                            tickfont=dict(color='#64748b', family='Inter, sans-serif')
                        ),
                        yaxis=dict(
                            title='',
                            tickfont=dict(color='#0f172a', size=12, family='Inter, sans-serif')
                        ),
                        plot_bgcolor='#ffffff',
                        paper_bgcolor='#ffffff',
                        font=dict(family='Inter, sans-serif')
                    )
                    st.plotly_chart(fig_p, use_container_width=True)
                else:
                    st.info("No projects matching current filter (All projects completed or filtered out)")

            with c_pdonut:
                if not df_proj.empty:
                    status_counts = df_proj['status'].value_counts().reset_index()
                    status_counts.columns = ['status', 'count']
                    color_map = {'Complete': '#10b981', 'In Progress': '#f59e0b', 'Not Started': '#cbd5e1'}
                    fig_pie = px.pie(
                        status_counts,
                        values='count',
                        names='status',
                        hole=0.62,
                        color='status',
                        color_discrete_map=color_map
                    )
                    fig_pie.update_layout(
                        height=240,
                        margin=dict(l=10, r=10, t=10, b=10),
                        legend=dict(orientation='h', yanchor='top', y=-0.1, xanchor='center', x=0.5, font=dict(color='#1e293b', size=12, family='Inter, sans-serif')),
                        paper_bgcolor='#ffffff',
                        annotations=[dict(
                            text=f'<span style="font-size:22px; font-weight:800; color:#0f172a;">{len(df_proj)}</span><br><span style="font-size:12px; color:#64748b; font-weight:600;">Projects</span>',
                            x=0.5, y=0.5,
                            showarrow=False
                        )],
                        font=dict(family='Inter, sans-serif')
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                    # Quick summary metrics
                    avg_progress = (df_proj['done'].sum() / df_proj['req'].sum() * 100) if df_proj['req'].sum() > 0 else 0.0
                    complete_n = sum(1 for r in proj_rows if r['status'] == 'Complete')
                    in_prog_n = sum(1 for r in proj_rows if r['status'] == 'In Progress')
                    not_start_n = sum(1 for r in proj_rows if r['status'] == 'Not Started')

                    st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px; margin-top:6px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
                            <span style="color:#64748b; font-weight:600;">Overall Completion Rate:</span>
                            <span style="font-weight:800; color:#0f172a; font-size:14px;">{avg_progress:.1f}%</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:13px;">
                            <span style="color:#059669; font-weight:600;">🟢 Complete:</span>
                            <span style="font-weight:700; color:#0f172a;">{complete_n} Projects</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px; font-size:13px;">
                            <span style="color:#d97706; font-weight:600;">🟡 In Progress:</span>
                            <span style="font-weight:700; color:#0f172a;">{in_prog_n} Projects</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:13px;">
                            <span style="color:#64748b; font-weight:600;">⚪ Not Started:</span>
                            <span style="font-weight:700; color:#0f172a;">{not_start_n} Projects</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # 3. CLEAN OVERVIEW TABLE (Without QG Milestone Columns and with Hide-Complete)
    # ----------------------------------------------------
    if any("Table" in str(v) or "3." in str(v) for v in (view_modes or [])):
        with st.container(border=True):
            s3_top1, s3_top2 = st.columns([3, 1], vertical_alignment="center")
            with s3_top1:
                st.markdown("#### 📋 3. Project Overview Table (Clean View)")
                st.caption("Streamlined project tracking table without Quality Gate milestone columns for clarity and focus")
            with s3_top2:
                hide_comp_s3 = st.toggle("Hide Complete", value=False, key="toggle_hide_comp_s3", help="Exclude completed projects from table")

            filtered_s3 = [p for p in filtered if p.get('calc_status') != 'Complete'] if hide_comp_s3 else filtered

            table_data = []
            for p in filtered_s3:
                prog_pct = p.get('calc_progress', 0.0) * 100
                st_val = p.get('calc_status', 'Not Started')
                st_icon = "🟢 Complete" if st_val == 'Complete' else ("🟡 In Progress" if st_val == 'In Progress' else "⚪ Not Started")
                table_data.append({
                    "No.": p.get('no') or p.get('row_idx', 0) - 3,
                    "Project No.": str(p.get('project_no', '')),
                    "Project Name": p.get('project_name', ''),
                    "PM": p.get('pm', '-'),
                    "Who?": p.get('who') or "Unassigned",
                    "Docs Done": int(p.get('calc_done', 0)),
                    "Docs Req": int(p.get('calc_req', 0)),
                    "Progress": prog_pct,
                    "Status": st_icon,
                    "Remark": p.get('remark') or "-"
                })

            df = pd.DataFrame(table_data)
            if not df.empty:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "No.": st.column_config.NumberColumn("No.", width="small"),
                        "Project No.": st.column_config.TextColumn("Project No.", width="small"),
                        "Project Name": st.column_config.TextColumn("Project Name", width="medium"),
                        "PM": st.column_config.TextColumn("PM", width="small"),
                        "Who?": st.column_config.TextColumn("Owner (Who?)", width="small"),
                        "Docs Done": st.column_config.NumberColumn("Docs Done", format="%d Docs", width="small"),
                        "Docs Req": st.column_config.NumberColumn("Docs Req", format="%d Docs", width="small"),
                        "Progress": st.column_config.ProgressColumn(
                            "Progress",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                            width="medium"
                        ),
                        "Status": st.column_config.TextColumn("Status", width="small"),
                        "Remark": st.column_config.TextColumn("Remark", width="medium"),
                    }
                )
            else:
                st.info("No projects found matching current filter criteria")

    st.divider()

    # Visual Milestone Cards & Gate Filter
    curr_cw = datetime.now().isocalendar()[1]
    
    import re
    def get_cw_num(val):
        if not val: return None
        m = re.search(r'CW\s*(\d+)', str(val), re.I)
        return int(m.group(1)) if m else None

    def get_current_gate(p):
        if p.get('calc_status') == 'Complete':
            return 'Complete', p.get('pl') or '-'
        gates = [('QG4', p.get('qg4')), ('QG5', p.get('qg5')), ('IFD', p.get('ifd')), ('FAT', p.get('fat')), ('PL', p.get('pl'))]
        for g_name, g_val in gates:
            g_num = get_cw_num(g_val)
            if g_num is not None and g_num >= curr_cw:
                return g_name, g_val
        for g_name, g_val in reversed(gates):
            if g_val:
                return g_name, g_val
        return 'QG4', '-'

    # Calculate current gate for every project
    for p in filtered:
        gate, cw = get_current_gate(p)
        p['current_gate'] = gate
        p['current_cw'] = cw

    # Header Row: Title on Left, CW Selector + Gate Filter Buttons (Pills) on Right (Image location)
    h_col_left, h_col_right = st.columns([1, 1], vertical_alignment="center")
    with h_col_left:
        st.subheader("📅 Project Quality Gate Timeline")
        st.caption("💡 Click on any **Project Title** on the card to open and edit its checklists directly.")
    with h_col_right:
        c_cw, c_pills = st.columns([1, 4], vertical_alignment="center")
        with c_cw:
            cw_options = ["All CW"] + [f"CW{w}" for w in range(1, 53)]
            default_cw_idx = cw_options.index(f"CW{curr_cw}") if f"CW{curr_cw}" in cw_options else 0
            selected_cw_str = st.selectbox(
                "Current CW",
                options=cw_options,
                index=default_cw_idx,
                label_visibility="collapsed",
                key="active_cw_select",
                help="📅 Select Calendar Week (Default: current ISO calendar week)"
            )
        with c_pills:
            gate_pills_val = st.pills(
                "Quality Gate Filter",
                options=["All", "QG4", "QG5", "IFD", "FAT", "PL", "Complete"],
                default="All",
                label_visibility="collapsed",
                key="gate_filter_pills"
            )

    selected_gate = gate_pills_val or "All"

    # Filter projects according to selected gate and selected_cw_str
    if selected_gate == "Complete":
        timeline_projects = [p for p in filtered if p.get('calc_status') == 'Complete']
    elif selected_gate in ["QG4", "QG5", "IFD", "FAT", "PL"]:
        gate_col = selected_gate.lower()
        if selected_cw_str == "All CW":
            timeline_projects = [p for p in filtered if p.get(gate_col)]
        else:
            timeline_projects = [
                p for p in filtered
                if str(p.get(gate_col, '')).strip().upper() == selected_cw_str.strip().upper()
            ]
    else:  # selected_gate == "All"
        timeline_projects = filtered

    # Information badge about current filter and week
    if selected_gate != "All":
        tag_bg = {
            'QG4': '#e0f2fe', 'QG5': '#e0f2fe', 'IFD': '#fef08a',
            'FAT': '#fed7aa', 'PL': '#bbf7d0', 'Complete': '#dcfce7'
        }.get(selected_gate, '#f1f5f9')
        tag_color = {
            'QG4': '#0369a1', 'QG5': '#0369a1', 'IFD': '#854d0e',
            'FAT': '#9a3412', 'PL': '#166534', 'Complete': '#15803d'
        }.get(selected_gate, '#334155')

        if selected_gate == "Complete":
            st.markdown(f"""
            <div style="background:{tag_bg}; color:{tag_color}; padding:6px 14px; border-radius:6px; font-size:13px; font-weight:600; margin-bottom:12px; display:inline-block; border:1px solid rgba(0,0,0,0.08);">
                🎯 Status: <b>Complete</b> : <b>{len(timeline_projects)} Projects</b>
            </div>
            """, unsafe_allow_html=True)
        elif selected_cw_str == "All CW":
            st.markdown(f"""
            <div style="background:{tag_bg}; color:{tag_color}; padding:6px 14px; border-radius:6px; font-size:13px; font-weight:600; margin-bottom:12px; display:inline-block; border:1px solid rgba(0,0,0,0.08);">
                🎯 Gate: <b>{selected_gate}</b> &nbsp;|&nbsp; All Weeks (All CW): <b>{len(timeline_projects)} Projects</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            proj_nos = [str(p.get('project_no')) for p in timeline_projects]
            matched_text = f" ({', '.join(proj_nos)})" if proj_nos else ""
            st.markdown(f"""
            <div style="background:{tag_bg}; color:{tag_color}; padding:6px 14px; border-radius:6px; font-size:13px; font-weight:600; margin-bottom:12px; display:inline-block; border:1px solid rgba(0,0,0,0.08);">
                🎯 Gate: <b>{selected_gate}</b> &nbsp;|&nbsp; Week <b>{selected_cw_str}</b>: <b>{len(timeline_projects)} Projects</b>{matched_text}
            </div>
            """, unsafe_allow_html=True)

    if not timeline_projects:
        if selected_gate == "Complete":
            st.info("ℹ️ No completed projects found")
        elif selected_cw_str == "All CW":
            st.info(f"ℹ️ No projects found with gate **{selected_gate}**")
        else:
            st.info(f"ℹ️ No projects found with gate **{selected_gate}** in week **{selected_cw_str}**")
    else:
        cols = st.columns(2)
        for i, p in enumerate(timeline_projects):
            proj_label = f"{p['project_no']} - {p['project_name']} (Row {p['row_idx']})"
            with cols[i % 2]:
                with st.container(border=True):
                    # Header row: Clickable Project Name (Left) and Status Badge (Right)
                    h_col1, h_col2 = st.columns([3, 1], vertical_alignment="center")
                    with h_col1:
                        if st.button(
                            f"📁 **{p.get('project_no')} - {p.get('project_name')}**",
                            key=f"proj_link_{p.get('row_idx')}_{p.get('project_no')}",
                            type="tertiary",
                            help="Click here to open and edit the Tracking Matrix (Checklists) for this project"
                        ):
                            st.session_state['pending_tab'] = "📋 Tracking Matrix (Checklists)"
                            st.session_state['tab2_proj_select'] = proj_label
                            st.rerun()
                    with h_col2:
                        st.markdown(f"""
                        <div style="text-align:right;">
                            <span class="badge-{'complete' if p.get('calc_status')=='Complete' else 'progress' if p.get('calc_status')=='In Progress' else 'notstarted'}">
                                {p.get('calc_status')}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style="font-size:13px; color:#64748b; margin:4px 0 10px 0;">
                        PM: <b>{p.get('pm')}</b> &nbsp;|&nbsp; Document Owner: <b>{p.get('who') or 'Unassigned'}</b> &nbsp;|&nbsp; Remark: <i>{p.get('remark') or 'None'}</i>
                    </div>
                    """, unsafe_allow_html=True)

                    # Milestone Badges with dynamic highlight
                    def badge_style(gate_name, bg, color, border_color):
                        is_hl = (selected_gate == gate_name) or (selected_gate == 'All' and p.get('current_gate') == gate_name)
                        if is_hl:
                            return f"background:{bg}; color:{color}; padding:3px 8px; border-radius:4px; border:2px solid {border_color}; font-weight:700; box-shadow:0 0 6px rgba(0,0,0,0.15);"
                        return f"background:{bg}; color:{color}; padding:3px 8px; border-radius:4px; border:1px solid transparent;"

                    b_qg4 = badge_style('QG4', '#e0f2fe', '#0369a1', '#0284c7')
                    b_qg5 = badge_style('QG5', '#e0f2fe', '#0369a1', '#0284c7')
                    b_ifd = badge_style('IFD', '#fef08a', '#854d0e', '#ca8a04')
                    b_fat = badge_style('FAT', '#fed7aa', '#9a3412', '#ea580c')
                    b_pl  = badge_style('PL',  '#bbf7d0', '#166534', '#16a34a')

                    st.markdown(f"""
                    <div style="display:flex; gap:6px; flex-wrap:wrap; font-size:12px; margin-bottom:10px; align-items:center;">
                        <span style="{b_qg4}"><b>QG4:</b> {p.get('qg4') or '-'}</span>
                        <span style="{b_qg5}"><b>QG5:</b> {p.get('qg5') or '-'}</span>
                        <span style="{b_ifd}"><b>IFD:</b> {p.get('ifd') or '-'}</span>
                        <span style="{b_fat}"><b>FAT:</b> {p.get('fat') or '-'}</span>
                        <span style="{b_pl}"><b>PL:</b> {p.get('pl') or '-'}</span>
                        <span style="font-size:11px; color:#64748b; margin-left:4px;">(Current Gate: <b>{p.get('current_gate')}</b>)</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:#475569; margin-bottom:4px;">
                        <span>Documentation Progress: {p.get('calc_done')}/{p.get('calc_req')} Docs</span>
                        <span><b>{p.get('calc_progress',0)*100:.1f}%</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(p.get('calc_progress', 0.0))

# ----------------------------------------------------
# TAB 2: TRACKING MATRIX (CHECKLIST EDITOR)
# ----------------------------------------------------
elif menu == "📋 Tracking Matrix (Checklists)":
    # Helper to calculate stats per category
    def get_category_stats(proj, category_key):
        items = [item for item in backend.CHECKLIST_ITEMS if item[2] == category_key]
        done = 0
        req = 0
        for key, _, _, _ in items:
            v = proj.get(key)
            if v is None or v == '' or str(v).strip().upper() == 'N/A':
                continue
            v_str = str(v).strip()
            if v == 1 or v_str in ['1', '1.0']:
                done += 1
                req += 1
            elif v == 0 or v_str in ['0', '0.0']:
                req += 1
            else:
                try:
                    float(v)
                    req += 1
                except ValueError:
                    pass
        pct = (done / req * 100) if req > 0 else 0.0
        return done, req, pct

    # Top Action & Breadcrumb Bar
    top_c1, top_c2, top_c3 = st.columns([1.2, 3.5, 1.3], vertical_alignment="center")
    with top_c1:
        if st.button("⬅️ Back to Dashboard", key="btn_back_to_dash", use_container_width=True):
            st.session_state['pending_tab'] = "📊 Dashboard & Metrics"
            st.rerun()
    with top_c2:
        st.markdown("<h3 style='margin:0; font-size:22px; color:#0f172a;'>📋 Project Tracking Matrix & Checklists</h3>", unsafe_allow_html=True)
        st.caption("Human-in-the-Loop Quality Gate Documentation Verification & Progress Control")
    with top_c3:
        if st.session_state['has_unsaved_changes']:
            if st.button("💾 Save to Excel Now", type="primary", use_container_width=True, help="Save changes to Master Excel immediately"):
                backup_path = backend.save_document_plan(projects, backend.DEFAULT_DOCUMENT_PLAN)
                st.session_state['has_unsaved_changes'] = False
                st.success(f"Saved! (Backup: {os.path.basename(backup_path)})")
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align:right;">
                <span style="background:#f0fdf4; color:#166534; font-size:12px; font-weight:700; padding:6px 12px; border-radius:8px; border:1px solid #bbf7d0;">
                    🟢 Master Excel Synced
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # Project Switcher & Quick Navigation Bar
    proj_map = {f"{p['project_no']} - {p['project_name']} (Row {p['row_idx']})": p for p in projects}
    proj_keys = list(proj_map.keys())

    if 'tab2_proj_select' not in st.session_state or st.session_state['tab2_proj_select'] not in proj_keys:
        st.session_state['tab2_proj_select'] = proj_keys[0] if proj_keys else ""

    curr_idx = proj_keys.index(st.session_state['tab2_proj_select']) if st.session_state['tab2_proj_select'] in proj_keys else 0

    def go_prev_proj():
        idx = proj_keys.index(st.session_state['tab2_proj_select']) if st.session_state['tab2_proj_select'] in proj_keys else 0
        if idx > 0:
            st.session_state['tab2_proj_select'] = proj_keys[idx - 1]

    def go_next_proj():
        idx = proj_keys.index(st.session_state['tab2_proj_select']) if st.session_state['tab2_proj_select'] in proj_keys else 0
        if idx < len(proj_keys) - 1:
            st.session_state['tab2_proj_select'] = proj_keys[idx + 1]

    def format_proj_option(opt):
        p = proj_map.get(opt)
        if not p: return opt
        st_icon = "🟢" if p.get('calc_status') == 'Complete' else ("🟡" if p.get('calc_status') == 'In Progress' else "⚪")
        return f"{st_icon} {p.get('project_no')} - {p.get('project_name')} | PM: {p.get('pm') or '-'} | Progress: {p.get('calc_progress', 0)*100:.0f}% ({p.get('calc_done')}/{p.get('calc_req')} Docs)"

    with st.container(border=True):
        nav_c1, nav_c2, nav_c3 = st.columns([1, 6, 1], vertical_alignment="center")
        with nav_c1:
            st.button("◀ Previous", disabled=curr_idx == 0, use_container_width=True, key="tab2_btn_prev", on_click=go_prev_proj, help="Switch to previous project")
        with nav_c2:
            selected_proj_label = st.selectbox(
                "Select Project to View & Edit",
                proj_keys,
                format_func=format_proj_option,
                key='tab2_proj_select',
                label_visibility="collapsed"
            )
        with nav_c3:
            st.button("Next ▶", disabled=curr_idx >= len(proj_keys) - 1, use_container_width=True, key="tab2_btn_next", on_click=go_next_proj, help="Switch to next project")

    curr_proj = proj_map.get(selected_proj_label, projects[0] if projects else None)

    if curr_proj:
        # Project Hero Card (Executive Summary Banner)
        status_color = {'Complete': '#15803d', 'In Progress': '#b45309', 'Not Started': '#64748b'}.get(curr_proj.get('calc_status'), '#64748b')
        status_bg = {'Complete': '#dcfce7', 'In Progress': '#fef3c7', 'Not Started': '#f1f5f9'}.get(curr_proj.get('calc_status'), '#f1f5f9')

        with st.container(border=True):
            hero_c1, hero_c2 = st.columns([1.8, 1.2], vertical_alignment="center")
            with hero_c1:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
                    <span style="font-size:24px; font-weight:800; color:#0f172a;">📁 {curr_proj.get('project_no')} - {curr_proj.get('project_name')}</span>
                    <span style="background:{status_bg}; color:{status_color}; padding:4px 12px; border-radius:9999px; font-weight:700; font-size:12px;">
                        {curr_proj.get('calc_status')}
                    </span>
                </div>
                <div style="font-size:13px; color:#475569; display:flex; gap:16px; flex-wrap:wrap; margin-bottom:10px;">
                    <span>👤 <b>PM:</b> {curr_proj.get('pm') or '-'}</span>
                    <span>📄 <b>Document Owner:</b> {curr_proj.get('who') or 'Unassigned'}</span>
                    <span>📝 <b>Remark:</b> <i>{curr_proj.get('remark') or 'None'}</i></span>
                </div>
                <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; font-size:12px;">
                    <span style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:6px; font-weight:600;"><b>QG4:</b> {curr_proj.get('qg4') or '-'}</span>
                    <span style="color:#94a3b8;">➔</span>
                    <span style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:6px; font-weight:600;"><b>QG5:</b> {curr_proj.get('qg5') or '-'}</span>
                    <span style="color:#94a3b8;">➔</span>
                    <span style="background:#fef08a; color:#854d0e; padding:4px 10px; border-radius:6px; font-weight:600;"><b>IFD:</b> {curr_proj.get('ifd') or '-'}</span>
                    <span style="color:#94a3b8;">➔</span>
                    <span style="background:#fed7aa; color:#9a3412; padding:4px 10px; border-radius:6px; font-weight:600;"><b>FAT:</b> {curr_proj.get('fat') or '-'}</span>
                    <span style="color:#94a3b8;">➔</span>
                    <span style="background:#bbf7d0; color:#166534; padding:4px 10px; border-radius:6px; font-weight:600;"><b>PL:</b> {curr_proj.get('pl') or '-'}</span>
                </div>
                """, unsafe_allow_html=True)

            with hero_c2:
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span style="font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px;">Overall Documentation</span>
                        <span style="font-size:18px; font-weight:800; color:#2563eb;">{curr_proj.get('calc_progress',0)*100:.1f}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:#475569; margin-bottom:6px;">
                        <span>Completed: <b>{curr_proj.get('calc_done', 0)} Docs</b></span>
                        <span>Required: <b>{curr_proj.get('calc_req', 0)} Docs</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(curr_proj.get('calc_progress', 0.0))

        # Category Breakdown KPI Banner
        qg4_done, qg4_req, qg4_pct = get_category_stats(curr_proj, 'QG4')
        ifd_done, ifd_req, ifd_pct = get_category_stats(curr_proj, 'IFD')
        final_done, final_req, final_pct = get_category_stats(curr_proj, 'FINAL')

        cat_col1, cat_col2, cat_col3 = st.columns(3)
        with cat_col1:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #2563eb; border-radius:10px; padding:12px 16px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; color:#1e40af; margin-bottom:4px;">
                    <span>🔷 QG4 DUE Phase</span>
                    <span>{qg4_done}/{qg4_req} ({qg4_pct:.0f}%)</span>
                </div>
                <div style="font-size:12px; color:#475569;">Target: <b style="color:#0f172a;">{curr_proj.get('qg4') or '-'}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(qg4_pct / 100.0)

        with cat_col2:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #f59e0b; border-radius:10px; padding:12px 16px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; color:#92400e; margin-bottom:4px;">
                    <span>🔶 IFD DUE Phase</span>
                    <span>{ifd_done}/{ifd_req} ({ifd_pct:.0f}%)</span>
                </div>
                <div style="font-size:12px; color:#475569;">Target: <b style="color:#0f172a;">{curr_proj.get('ifd') or '-'}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(ifd_pct / 100.0)

        with cat_col3:
            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-top:3px solid #10b981; border-radius:10px; padding:12px 16px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:700; color:#065f46; margin-bottom:4px;">
                    <span>🟢 FINAL DUE (PL) Phase</span>
                    <span>{final_done}/{final_req} ({final_pct:.0f}%)</span>
                </div>
                <div style="font-size:12px; color:#475569;">Target: <b style="color:#0f172a;">{curr_proj.get('pl') or '-'}</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(final_pct / 100.0)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        def format_val_to_choice(val):
            if val is None or str(val).strip().upper() == 'N/A':
                return "⚪ N/A"
            if str(val).strip() in ['1', '1.0']:
                return "🟢 1 (Done)"
            if str(val).strip() in ['0', '0.0']:
                return "🟡 0 (WIP)"
            return "⚪ N/A"

        def choice_to_val(choice):
            if "Done" in str(choice) or "1" in str(choice):
                return 1
            elif "WIP" in str(choice) or "0" in str(choice):
                return 0
            return "N/A"

        choice_options = ["🟢 1 (Done)", "🟡 0 (WIP)", "⚪ N/A"]

        # Form for editing project details & checklist matrix
        with st.form(key=f"edit_form_{curr_proj['project_no']}"):
            # Card A: Project Metadata & Milestones Schedule
            with st.container(border=True):
                st.markdown("""
                <div style="background: linear-gradient(90deg, #f8fafc 0%, #ffffff 100%); border-left: 6px solid #4f46e5; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 15px; font-weight: 800; color: #1e1b4b;">⚙️ Project Metadata & Milestone Delivery Schedule</span>
                    <span style="background: #eef2ff; color: #4338ca; font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 6px; border: 1px solid #c7d2fe;">Schedule & Ownership</span>
                </div>
                """, unsafe_allow_html=True)
                g1, g2, g3 = st.columns([1, 1, 1.5])
                with g1:
                    pm_val = st.text_input("PM (Project Manager)", value=curr_proj.get('pm') or "", help="Responsible Project Manager")
                with g2:
                    who_val = st.text_input("Who? (Document Owner)", value=curr_proj.get('who') or "", help="Person responsible for document deliverables")
                with g3:
                    remark_val = st.text_input("Remark (Notes)", value=curr_proj.get('remark') or "", help="Project documentation remarks or notes")

                st.markdown("""
                <div style="margin: 14px 0 8px 0; font-size: 13px; font-weight: 700; color: #334155; display: flex; align-items: center; gap: 6px;">
                    <span>🗓️ Quality Gate Milestones (Calendar Week):</span>
                </div>
                """, unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1:
                    qg4_val = st.text_input("QG4 (CW)", value=curr_proj.get('qg4') or "", placeholder="e.g. CW40")
                with m2:
                    qg5_val = st.text_input("QG5 (CW)", value=curr_proj.get('qg5') or "", placeholder="e.g. CW42")
                with m3:
                    ifd_val = st.text_input("IFD (CW)", value=curr_proj.get('ifd') or "", placeholder="e.g. CW44")
                with m4:
                    fat_val = st.text_input("FAT (CW)", value=curr_proj.get('fat') or "", placeholder="e.g. CW46")
                with m5:
                    pl_val = st.text_input("PL (CW)", value=curr_proj.get('pl') or "", placeholder="e.g. CW48")

            updated_checklists = {}

            # Card B: 1. QG4 Checklist
            qg4_items = [item for item in backend.CHECKLIST_ITEMS if item[2] == 'QG4']
            with st.container(border=True):
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #f0f9ff 0%, #ffffff 100%); border-left: 6px solid #2563eb; border-top: 1px solid #bae6fd; border-right: 1px solid #bae6fd; border-bottom: 1px solid #bae6fd; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 15px; font-weight: 800; color: #1e40af;">🔷 1. QG4 DUE: Initial Testing & Concept Documents</span>
                    <span style="background: #2563eb; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 14px; border-radius: 9999px; box-shadow: 0 1px 3px rgba(37,99,235,0.3);">
                        Done: {qg4_done}/{qg4_req} Docs ({qg4_pct:.0f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)

                qg4_cols = st.columns(4)
                for idx, (key, label, _, desc) in enumerate(qg4_items):
                    with qg4_cols[idx % 4]:
                        current_c = format_val_to_choice(curr_proj.get(key))
                        updated_checklists[key] = st.selectbox(
                            f"{label}",
                            choice_options,
                            index=choice_options.index(current_c),
                            key=f"{curr_proj['project_no']}_{key}",
                            help=desc
                        )

            # Card C: 2. IFD Checklist
            ifd_items = [item for item in backend.CHECKLIST_ITEMS if item[2] == 'IFD']
            with st.container(border=True):
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #fffbeb 0%, #ffffff 100%); border-left: 6px solid #d97706; border-top: 1px solid #fde68a; border-right: 1px solid #fde68a; border-bottom: 1px solid #fde68a; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 15px; font-weight: 800; color: #92400e;">🔶 2. IFD DUE: Factory Delivery & Integration Documents</span>
                    <span style="background: #d97706; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 14px; border-radius: 9999px; box-shadow: 0 1px 3px rgba(217,119,6,0.3);">
                        Done: {ifd_done}/{ifd_req} Docs ({ifd_pct:.0f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)

                ifd_cols = st.columns(4)
                for idx, (key, label, _, desc) in enumerate(ifd_items):
                    with ifd_cols[idx % 4]:
                        current_c = format_val_to_choice(curr_proj.get(key))
                        updated_checklists[key] = st.selectbox(
                            f"{label}",
                            choice_options,
                            index=choice_options.index(current_c),
                            key=f"{curr_proj['project_no']}_{key}",
                            help=desc
                        )

            # Card D: 3. FINAL Checklist
            final_items = [item for item in backend.CHECKLIST_ITEMS if item[2] == 'FINAL']
            with st.container(border=True):
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #ecfdf5 0%, #ffffff 100%); border-left: 6px solid #059669; border-top: 1px solid #a7f3d0; border-right: 1px solid #a7f3d0; border-bottom: 1px solid #a7f3d0; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 15px; font-weight: 800; color: #065f46;">🟢 3. FINAL DUE (PL): Handover & Acceptance Documents</span>
                    <span style="background: #059669; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 14px; border-radius: 9999px; box-shadow: 0 1px 3px rgba(5,150,105,0.3);">
                        Done: {final_done}/{final_req} Docs ({final_pct:.0f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)

                final_cols = st.columns(5)
                for idx, (key, label, _, desc) in enumerate(final_items):
                    with final_cols[idx % 5]:
                        current_c = format_val_to_choice(curr_proj.get(key))
                        updated_checklists[key] = st.selectbox(
                            f"{label}",
                            choice_options,
                            index=choice_options.index(current_c),
                            key=f"{curr_proj['project_no']}_{key}",
                            help=desc
                        )

            st.divider()

            submit_col1, submit_col2 = st.columns([2, 1], vertical_alignment="center")
            with submit_col1:
                submit_btn = st.form_submit_button("💾 Save Project Checklists (Update in Memory)", type="primary", use_container_width=True)
            with submit_col2:
                st.caption("Updates metrics and formulas immediately. Remember to click 'Save to Excel' to write to file.")

            if submit_btn:
                curr_proj['pm'] = pm_val
                curr_proj['who'] = who_val
                curr_proj['remark'] = remark_val
                curr_proj['qg4'] = qg4_val
                curr_proj['qg5'] = qg5_val
                curr_proj['ifd'] = ifd_val
                curr_proj['fat'] = fat_val
                curr_proj['pl'] = pl_val

                for k, choice in updated_checklists.items():
                    curr_proj[k] = choice_to_val(choice)

                # Recalculate
                done, req, prog, status = backend.calculate_metrics(curr_proj)
                curr_proj['calc_done'] = done
                curr_proj['calc_req'] = req
                curr_proj['calc_progress'] = prog
                curr_proj['calc_status'] = status

                st.session_state['has_unsaved_changes'] = True
                st.success(f"✅ Successfully updated project {curr_proj['project_no']} ({curr_proj['project_name']})! Progress: {prog*100:.1f}% ({done}/{req} Docs)")
                st.rerun()

# ----------------------------------------------------
# TAB 3: DELIVERY OVERVIEW SYNC CENTER
# ----------------------------------------------------
elif menu == "🔄 Delivery Overview Sync":
    st.subheader("🔄 Delivery Overview Import & Maintenance Center")
    st.markdown("""
    The system reads project details and Quality Gate delivery milestones (`CW`) from the **Delivery Overview** file,
    then automatically updates columns **A-D, F-K, T, Y, AE-AH** while **preserving 100% of existing checklist item records**.
    """)

    sync_col1, sync_col2 = st.columns([1, 1])

    with sync_col1:
        st.markdown("#### Method 1: Drag & Drop or Upload New File")
        uploaded_file = st.file_uploader(
            "Select Delivery Overview File (.xlsx)",
            type=["xlsx"],
            key="delivery_uploader",
            help="Upload the latest Delivery Overview .xlsx file"
        )

    with sync_col2:
        st.markdown("#### Method 2: Use Default File in Folder")
        default_file_ready = os.path.exists(backend.DEFAULT_DELIVERY_OVERVIEW)
        st.write(f"Local file: `{os.path.basename(backend.DEFAULT_DELIVERY_OVERVIEW)}`")
        use_local_btn = st.button("📂 Load Data from Default File in Folder", disabled=not default_file_ready)

    overview_source = None
    if uploaded_file is not None:
        overview_source = io.BytesIO(uploaded_file.getvalue())
        st.info(f"📄 Reading uploaded file: **{uploaded_file.name}**")
    elif use_local_btn and default_file_ready:
        overview_source = backend.DEFAULT_DELIVERY_OVERVIEW
        st.info(f"📄 Reading default file: **{os.path.basename(backend.DEFAULT_DELIVERY_OVERVIEW)}**")

    if overview_source is not None:
        with st.spinner("Parsing project milestones and timeline data..."):
            parsed_overview = backend.parse_delivery_overview(overview_source)
            st.session_state['parsed_overview'] = parsed_overview

    if 'parsed_overview' in st.session_state:
        parsed_overview = st.session_state['parsed_overview']
        st.success(f"🎉 Detected **{len(parsed_overview)} projects** in Delivery Overview file")

        # Preview comparison
        st.markdown("### 🔍 Sync Preview & Validation")

        preview_rows = []
        for o in parsed_overview:
            matched_proj, match_type = backend.find_best_project_match(o, projects)
            if matched_proj:
                action = "🔄 Update" if match_type == 'exact' else f"🔗 Link ({matched_proj['project_no']})"
            else:
                action = "➕ Add New"

            preview_rows.append({
                "Action": action,
                "Delivery Proj No.": o['project_no'],
                "Matched Plan No.": matched_proj['project_no'] if matched_proj else "New Project",
                "Project Name": o['project_name'],
                "PM": o['pm'],
                "QG4 (CW)": o['qg4'] or "-",
                "QG5 (CW)": o['qg5'] or "-",
                "IFD (CW)": o['ifd'] or "-",
                "FAT (CW)": o['fat'] or "-",
                "PL (CW)": o['pl'] or "-",
            })

        st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

        col_opt1, col_opt2 = st.columns([1, 1])
        with col_opt1:
            match_mode = st.radio(
                "Project Matching Strategy",
                ["Smart Matching (Fuzzy matching with automatic code normalization)", "Exact Match Only (100% identical project codes)"],
                index=0
            )
        with col_opt2:
            auto_save_checked = st.checkbox(
                "💾 Automatically overwrite Master Excel (PD207_Document_Plan_Filled_Status.xlsx) immediately",
                value=True,
                help="When clicking the button below, results will be written to Excel immediately with an automated backup created"
            )

        st.divider()
        if st.button("⚡ Execute Sync & Update Plan", type="primary", use_container_width=True):
            strategy = 'smart' if "Smart" in match_mode else 'exact'
            updated_projs, sync_logs = backend.sync_projects(projects, parsed_overview, match_strategy=strategy)
            st.session_state['projects'] = updated_projs
            st.session_state['sync_logs'] = sync_logs
            st.session_state['has_unsaved_changes'] = not auto_save_checked

            if auto_save_checked:
                bk_file = backend.save_document_plan(updated_projs, backend.DEFAULT_DOCUMENT_PLAN)
                st.session_state['has_unsaved_changes'] = False
                st.balloons()
                st.success(f"✅ Successfully synced and saved to Master Excel! (Backup: {os.path.basename(bk_file)})")
            else:
                st.balloons()
                st.success("✅ Synchronization successful in memory! (Navigate to Save & Export to write to file or download)")

            # Provide instant download right here!
            instant_bytes = backend.export_document_plan_bytes(updated_projs, backend.DEFAULT_DOCUMENT_PLAN)
            ts_instant = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Download Synced Excel (.xlsx)",
                data=instant_bytes,
                file_name=f"PD207_Document_Plan_Synced_{ts_instant}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.rerun()

    # Show past sync logs
    if st.session_state['sync_logs']:
        with st.expander("📜 Recent Sync History (Audit Logs)", expanded=True):
            for l in st.session_state['sync_logs']:
                st.write(f"- **[{l['action']}]** {l['details']}")

# ----------------------------------------------------
# TAB 4: SAVE & EXPORT CENTER
# ----------------------------------------------------
elif menu == "💾 Save & Export Excel":
    st.subheader("💾 Save & Export Center")
    st.markdown("""
    Key Highlights: The system writes back into the Excel file while **preserving all 602 original formulas (LET, COUNTIF, IF, IFERROR)**, 
    colors, cell borders, and sheet formatting 100%. An **Automated Backup** is created every time changes are saved.
    """)

    st.write(f"📂 **Target Master File:** `{backend.DEFAULT_DOCUMENT_PLAN}`")
    st.write(f"📊 **Current Projects in System:** **{len(projects)} Projects**")

    if st.session_state['has_unsaved_changes']:
        st.warning("⚠️ You have unsaved changes in the App that have not yet been written to Master Excel")
    else:
        st.success("🟢 Excel file is up to date and synchronized with current view")

    save_c1, save_c2 = st.columns(2)

    with save_c1:
        st.markdown("#### 1. Save Directly to Master Excel")
        st.caption("Overwrite `PD207_Document_Plan_Filled_Status.xlsx` in the project directory immediately")
        if st.button("💾 Save to Master Excel", type="primary", use_container_width=True):
            with st.spinner("Saving changes and creating automated backup..."):
                try:
                    backup_path = backend.save_document_plan(projects, backend.DEFAULT_DOCUMENT_PLAN)
                    st.session_state['has_unsaved_changes'] = False
                    st.success(f"✅ Successfully saved! {len(projects)} projects updated in Master Excel")
                    st.info(f"🛡️ Automated backup created: `{os.path.basename(backup_path)}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ An error occurred while saving: {e}")

    with save_c2:
        st.markdown("#### 2. Download as New Excel File")
        st.caption(f"Download the Excel (.xlsx) file containing {len(projects)} projects with full formula preservation")
        excel_bytes = backend.export_document_plan_bytes(projects, backend.DEFAULT_DOCUMENT_PLAN)
        ts_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"PD207_Document_Plan_Updated_{ts_now}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    # Backups history
    st.subheader("🛡️ Backup History")
    backup_dir = os.path.join(os.path.dirname(backend.DEFAULT_DOCUMENT_PLAN), "backups")
    if os.path.exists(backup_dir):
        backups = sorted(os.listdir(backup_dir), reverse=True)
        if backups:
            for b in backups[:10]:
                b_path = os.path.join(backup_dir, b)
                sz = os.path.getsize(b_path) // 1024
                st.write(f"- 📄 `{b}` ({sz} KB)")
        else:
            st.caption("No backup history yet (created automatically on first save)")
    else:
        st.caption("The Backups folder will be created automatically upon first save")
