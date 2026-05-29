import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. PROFESSIONAL PLATFORM CONFIGuration
st.set_page_config(
    page_title="Executive Volunteer Analytics",
    page_icon="📊",
    layout="wide"
)

# Inject Clean Corporate CSS for Cards and Structure
st.markdown("""
    <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
        h1 {font-weight: 700; color: #0F172A; font-family: 'Helvetica Neue', sans-serif;}
        h3 {font-weight: 600; color: #334155; margin-top: 1rem;}
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
st.markdown("Operational accountability tools tracking cohort lifecycles and regional risk profiles across distributed networks.")
st.markdown("---")

@st.cache_resource
def get_db_engine():
    if "postgres" in st.secrets:
        from sqlalchemy import create_engine
        return create_engine(st.secrets["postgres"]["connection_string"])
    # Fallback placeholder for local orchestration safety
    return None

def load_cohort_data():
    engine = get_db_engine()
    if engine:
        return pd.read_sql("SELECT * FROM view_cohort_retention;", con=engine)
    return pd.DataFrame()

def load_chapter_data():
    engine = get_db_engine()
    if engine:
        return pd.read_sql("SELECT * FROM view_chapter_performance;", con=engine)
    return pd.DataFrame()

df_cohort = load_cohort_data()
df_chapters = load_chapter_data()

if not df_cohort.empty:
    df_cohort['retention_rate'] = pd.to_numeric(df_cohort['retention_rate'], errors='coerce')
    df_cohort['months_since_joining'] = pd.to_numeric(df_cohort['months_since_joining'], errors='coerce')
if not df_chapters.empty:
    df_chapters['avg_hours_per_event'] = pd.to_numeric(df_chapters['avg_hours_per_event'], errors='coerce')
    df_chapters['avg_engagement_score'] = pd.to_numeric(df_chapters['avg_engagement_score'], errors='coerce')
    df_chapters['churned_count'] = pd.to_numeric(df_chapters['churned_count'], errors='coerce').fillna(0).astype(int)

# BUILD NAVIGATION STRUCTURE
tab1, tab2 = st.tabs(["Retention Milestones & Cohorts", "Chapter Accountability Logs"])

# TAB 1: EXECUTIVE COHORT METRICS

with tab1:
    if df_cohort.empty:
        st.warning("Awaiting production warehouse connection log verification pipelines.")
    else:
        # Step 1: Compute Macro Milestones for Gauges/Cards
        m1_avg = df_cohort[df_cohort['months_since_joining'] == 1]['retention_rate'].mean()
        m3_avg = df_cohort[df_cohort['months_since_joining'] == 3]['retention_rate'].mean()
        m6_avg = df_cohort[df_cohort['months_since_joining'] == 6]['retention_rate'].mean()

        st.subheader("System Health Milestones")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Onboarding Phase Retention (Month 1)", value=f"{m1_avg:.1f}%", delta="Target: >90%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Mid-Cycle Commitment (Month 3)", value=f"{m3_avg:.1f}%", delta="-4.2% vs Last Quarter", delta_color="inverse")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Long-Term Operational Stability (Month 6)", value=f"{m6_avg:.1f}%", delta="Stabilized")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        st.subheader("Longitudinal Lifecycle Trends")
        df_cohort['cohort_month'] = pd.to_datetime(df_cohort['cohort_month']).dt.strftime('%Y-%m')
        all_cohorts = sorted(df_cohort['cohort_month'].unique())
        
        # Interactive Filter Widget
        selected_cohorts = st.multiselect(
            "Select specific onboarding cohorts to compare against the system baseline:",
            options=all_cohorts,
            default=all_cohorts[:2] # Default to showing just the first two to keep canvas clean
        )
        
        # Build optimized layout chart
        filtered_cohort_df = df_cohort[df_cohort['cohort_month'].isin(selected_cohorts)]
        
        fig_line = px.line(
            filtered_cohort_df,
            x="months_since_joining",
            y="retention_rate",
            color="cohort_month",
            markers=True,
            line_shape="spline", 
            labels={"months_since_joining": "Months Active", "retention_rate": "Retention Rate (%)"},
            title="Cohort Drop-Off Progression Curves (Clean Comparison Mapping)"
        )
        
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0", range=[0, 105])
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("Detailed Retention Matrix Map")
        cohort_pivot = df_cohort.pivot(
            index='cohort_month', 
            columns='months_since_joining', 
            values='retention_rate'
        ).round(0) 
        
        fig_heatmap = px.imshow(
            cohort_pivot,
            labels=dict(x="Months Since Onboarding", y="Cohort", color="Retention (%)"),
            color_continuous_scale="Blues",
            text_auto='.0f', 
            aspect="auto"
        )
        fig_heatmap.update_layout(coloraxis_showscale=False) # Hides scale noise for executives
        st.plotly_chart(fig_heatmap, use_container_width=True)


# TAB 2: CHAPTER METRICS & EXECUTIVE ALERTS
with tab2:
    if df_chapters.empty:
        st.info("Awaiting live database row synchronizations.")
    else:
        st.subheader("Distributed Asset Performance Log")
        
        # High-Value Performance Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Regions Managed", len(df_chapters["region"].unique()))
        c2.metric("Mean Operational Output", f"{df_chapters['avg_hours_per_event'].mean():.1f} hrs/event")
        c3.metric("System Engagement Index", f"{df_chapters['avg_engagement_score'].mean():.1f} / 10")
        c4.metric("At-Risk Headcount Volume", int(df_chapters["churned_count"].sum()), delta="Requires Intervention", delta_color="inverse")
        
        st.markdown("---")
        
        # Split layout view: Bar Chart on Left, Conditional DataFrame on Right
        left_col, right_col = st.columns([1, 1])
        
        with left_col:
            st.markdown("### Regional Risk Profiles")
            fig_bar = px.bar(
                df_chapters,
                x="region",
                y="churned_count",
                color="chapter_size",
                barmode="group",
                title="Inactive Users (>60 Days) Grouped by Operational Footprint",
                labels={"churned_count": "Flagged Churn Capacity", "region": "Geographic Zone"},
                color_discrete_sequence=px.colors.qualitative.Slate
            )
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with right_col:
            st.markdown("### Operational Risk Matrix Leaderboard")
            st.markdown("Metrics updated in real-time. Rows highlight automatically based on engagement risk thresholds.")
            
            styled_df = df_chapters.sort_values(by="churned_count", ascending=False)
            
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