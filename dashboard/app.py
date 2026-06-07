import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ==========================================
# 1. ENTERPRISE PLATFORM CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Executive Volunteer Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
        h1 {font-weight: 700; color: #0F172A; font-family: 'Helvetica Neue', sans-serif;}
        h3 {font-weight: 600; color: #334155; margin-top: 1.25rem;}
        .metric-card {
            background-color: #FFFFFF; 
            padding: 1.25rem; 
            border-radius: 0.75rem; 
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

st.title("Strategic Volunteer Retention Command Center")
st.markdown("Operational accountability tracking across distributed geographic networks drawing natively from localized data warehouse pipelines.")
st.markdown("---")


# ==========================================
# 2. ASYNCHRONOUS HIGH-PERFORMANCE DATA PIPELINE
# ==========================================
@st.cache_resource
def get_db_engine():
    """Establishes and caches a global database connection pool."""
    if "postgres" in st.secrets:
        return create_engine(st.secrets["postgres"]["connection_string"])
    # Local fallback option
    return create_engine("postgresql+psycopg2://yani@localhost:5432/volunteer_analytics")


@st.cache_data(ttl=600)
def load_cached_cohort_data():
    """Fetches cohort records and maps types in-memory to prevent click lag."""
    engine = get_db_engine()
    df = pd.read_sql("SELECT * FROM view_cohort_retention;", con=engine)
    if not df.empty:
        df['retention_rate'] = pd.to_numeric(df['retention_rate'], errors='coerce')
        df['months_since_joining'] = pd.to_numeric(df['months_since_joining'], errors='coerce')
        df['parsed_date'] = pd.to_datetime(df['cohort_month'])
        df['cohort_month'] = df['parsed_date'].dt.strftime('%Y-%m')
        df['cohort_year'] = df['parsed_date'].dt.strftime('%Y')
    return df


@st.cache_data(ttl=600)
def load_cached_chapter_data():
    """Fetches chapter records and handles clean numeric conversion schemas."""
    engine = get_db_engine()
    df = pd.read_sql("SELECT * FROM view_chapter_performance;", con=engine)
    if not df.empty:
        df['avg_hours_per_event'] = pd.to_numeric(df['avg_hours_per_event'], errors='coerce')
        df['avg_engagement_score'] = pd.to_numeric(df['avg_engagement_score'], errors='coerce')
        df['churned_count'] = pd.to_numeric(df['churned_count'], errors='coerce').fillna(0).astype(int)
    return df


# Ingest datasets cleanly from cache functions
df_cohort = load_cached_cohort_data()
df_chapters = load_cached_chapter_data()


# ==========================================
# 3. INTERACTIVE NAVIGATION LAYER
# ==========================================
tab1, tab2 = st.tabs(["Retention Milestones & Cohorts", "Chapter Accountability Logs"])


# ==========================================
# TAB 1: EXECUTIVE COHORT METRICS
# ==========================================
with tab1:
    if df_cohort.empty:
        st.warning("Awaiting production data warehouse synchronization log validations.")
    else:
        # Compute Macro Conversion Benchmarks
        m1_avg = df_cohort[df_cohort['months_since_joining'] == 1]['retention_rate'].mean()
        m3_avg = df_cohort[df_cohort['months_since_joining'] == 3]['retention_rate'].mean()
        m6_avg = df_cohort[df_cohort['months_since_joining'] == 6]['retention_rate'].mean()

        st.subheader("System Health Milestones")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            with st.container(border=True):
                st.metric("Active Regions Managed", len(df_chapters["region"].unique()))
                
        with c2:
            with st.container(border=True):
                st.metric("Mean Operational Output", f"{df_chapters['avg_hours_per_event'].mean():.1f} hrs/event")
                
        with c3:
            with st.container(border=True):
                st.metric("System Engagement Index", f"{df_chapters['avg_engagement_score'].mean():.1f} / 10")
                
        with c4:
            with st.container(border=True):
                st.metric("At-Risk Headcount Volume", int(df_chapters["churned_count"].sum()), delta="Requires Attention", delta_color="inverse")
        st.markdown("---")
        
        # Hierarchical Controls: Split selectors to filter cohort context
        st.subheader("Longitudinal Lifecycle Trends")
        filter_col1, filter_col2 = st.columns([1, 3])
        
        with filter_col1:
            available_years = sorted(df_cohort['cohort_year'].unique(), reverse=True)
            selected_year = st.selectbox("Focus Year Context", options=["All Years"] + available_years)
        
        # Dynamically restrict multiselect options based on selected context year
        if selected_year == "All Years":
            filtered_cohort_options = sorted(df_cohort['cohort_month'].unique())
        else:
            filtered_cohort_options = sorted(df_cohort[df_cohort['cohort_year'] == selected_year]['cohort_month'].unique())
            
        with filter_col2:
            selected_cohorts = st.multiselect(
                "Select Cohort Batches to Benchmark:",
                options=filtered_cohort_options,
                default=filtered_cohort_options[:2]
            )

        # Build Rolling System-Wide Average Baseline Track
        baseline_df = df_cohort.groupby('months_since_joining')['retention_rate'].mean().reset_index()
        
        fig_line = go.Figure()
        
        # Add Organizational Baseline Trace
        fig_line.add_trace(
            go.Scattergl(
                x=baseline_df["months_since_joining"],
                y=baseline_df["retention_rate"],
                name="System Historical Baseline",
                mode='lines',
                line=dict(color='#94A3B8', width=4, dash='dash'),
                opacity=0.8
            )
        )
        
        # Map Hardware-Accelerated Interactive WebGL Curves
        premium_palette = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]
        filtered_cohort_df = df_cohort[df_cohort['cohort_month'].isin(selected_cohorts)]
        
        for i, cohort in enumerate(selected_cohorts):
            cohort_data = filtered_cohort_df[filtered_cohort_df['cohort_month'] == cohort].sort_values('months_since_joining')
            if not cohort_data.empty:
                fig_line.add_trace(
                    go.Scattergl(
                        x=cohort_data["months_since_joining"],
                        y=cohort_data["retention_rate"],
                        name=f"Cohort {cohort}",
                        mode='lines+markers',
                        # 🚀 FIX: Removed shape='spline' to satisfy WebGL GPU requirements
                        line=dict(color=premium_palette[i % len(premium_palette)], width=3), 
                        marker=dict(size=7)
                    )
                )
        
        fig_line.update_layout(
            title="Cohort Performance vs. Rolling Organizational Baseline",
            xaxis_title="Timeline Progression (Months Elapsed)",
            yaxis_title="Retention Percentage (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickmode='linear', dtick=1),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", range=[0, 105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")
        
        # Rounded Analytical Matrix Map
        st.subheader("Granular Retention Matrix Map")
        cohort_pivot = df_cohort.pivot(
            index='cohort_month', 
            columns='months_since_joining', 
            values='retention_rate'
        ).round(0)
        
        fig_heatmap = px.imshow(
            cohort_pivot,
            labels=dict(x="Months Active", y="Cohort Group", color="Retention (%)"),
            color_continuous_scale="Blues",
            text_auto='.0f',
            aspect="auto"
        )
        fig_heatmap.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_heatmap, use_container_width=True)


# ==========================================
# TAB 2: CHAPTER METRICS & EXECUTIVE ALERTS
# ==========================================
with tab2:
    if df_chapters.empty:
        st.info("Awaiting live cloud data warehouse synchronizations.")
    else:
        st.subheader("Distributed Asset Performance Log")
        
        # KPI Rows
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            with st.container(border=True):
                st.metric("Active Chapters Managed", len(df_chapters))
        with c2:
            with st.container(border=True):
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Mean Operational Output", f"{df_chapters['avg_hours_per_event'].mean():.1f} hrs/event")
                st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            with st.container(border=True):
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("System Engagement Index", f"{df_chapters['avg_engagement_score'].mean():.1f} / 10")
            st.markdown('</div>', unsafe_allow_html=True)
        with c4:
            with st.container(border=True):
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("At-Risk Headcount Volume", int(df_chapters["churned_count"].sum()), delta="Requires Attention", delta_color="inverse")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Split Operational Panel Layout
        left_col, right_col = st.columns([1, 1])
        
        with left_col:
            st.markdown("### Regional Risk Profiles")
            executive_slate_palette = ["#334155", "#64748B", "#94A3B8", "#CBD5E1"]
            
            fig_bar = px.bar(
                df_chapters,
                x="region",
                y="churned_count",
                color="chapter_size",
                barmode="group",
                title="Inactive Users (>60 Days) Grouped by Operational Footprint",
                labels={"churned_count": "Flagged Churn Capacity", "region": "Geographic Zone"},
                color_discrete_sequence=executive_slate_palette
            )
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#E2E8F0")
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with right_col:
            st.markdown("### Operational Risk Matrix Leaderboard")
            st.markdown("Metrics updated in real-time. Native column arrays monitor high-risk thresholds.")
            
            styled_df = df_chapters.sort_values(by="churned_count", ascending=False)
            
            # Interactive Data Frame Editor with built-in visualization progress track
            st.data_editor(
                styled_df,
                column_config={
                    "chapter_id": "Chapter Code",
                    "region": "Region Location",
                    "chapter_size": "Scale Tier",
                    "total_assigned_volunteers": "Total Staff",
                    "avg_hours_per_event": "Avg Event Hours",
                    "avg_engagement_score": st.column_config.ProgressColumn(
                        "Engagement Index",
                        help="Mean volunteer feedback rating",
                        format="%.2f",
                        min_value=0,
                        max_value=10,
                    ),
                    "churned_count": "At-Risk Users Count"
                },
                disabled=True,
                hide_index=True,
                use_container_width=True
            )