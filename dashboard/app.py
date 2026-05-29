import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

st.set_page_config(
    page_title="Volunteer Analytics Platform",
    layout="wide"
)

st.title("Strategic Volunteer Retention & Operational Analytics")
st.markdown("Automated insights engine drawing natively from localized data warehouse pipelines.")
st.markdown("---")

@st.cache_resource
def get_db_engine():
    return create_engine("postgresql+psycopg2://yani@localhost:5432/volunteer_analytics")

engine = get_db_engine()

# 3. TAB STRUCTURE
tab1, tab2 = st.tabs(["Cohort Retention Heatmap Matrix", "Regional Chapter Performance Metrics"])

#Executive Cohort Retention Analysis
with tab1:
    st.subheader("Onboarding Cohort Life-Cycle Decay")
    st.markdown("This matrix tracks retention percentage decay over time. **Deep blue fields represent stable engagement; fading boxes expose structural churn points.**")
    
    try:
        df_cohort = pd.read_sql("SELECT * FROM view_cohort_retention;", con=engine)
        
        if df_cohort.empty:
            st.warning("Cohort view returned clean but empty. Verify fact ingestion logs.")
        else:
            # Pivot the flat SQL rows into a classic 2D Cohort Matrix Grid
            df_cohort['cohort_month'] = pd.to_datetime(df_cohort['cohort_month']).dt.strftime('%Y-%m')
            cohort_pivot = df_cohort.pivot(
                index='cohort_month', 
                columns='months_since_joining', 
                values='retention_rate'
            )
            
            # Render a professional, clean Heatmap Matrix using Plotly
            fig_heatmap = px.imshow(
                cohort_pivot,
                labels=dict(x="Months Since Onboarding", y="Onboarding Cohort", color="Retention Rate (%)"),
                x=cohort_pivot.columns,
                y=cohort_pivot.index,
                color_continuous_scale="Blues", # Clean corporate color palette
                text_auto=True, # Overlays the exact percentages automatically
                aspect="auto"
            )
            
            fig_heatmap.update_layout(
                xaxis_title="Timeline Progression (Months Elapsed)",
                yaxis_title="Cohort Joining Month",
                coloraxis_showscale=True
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Structured progression line graph as a sub-insight
            st.markdown("### Longitudinal Retention Curves")
            fig_line = px.line(
                df_cohort,
                x="months_since_joining",
                y="retention_rate",
                color="cohort_month",
                markers=True,
                line_shape="linear",
                labels={"months_since_joining": "Months Since Joining", "retention_rate": "Retention (%)"}
            )
            st.plotly_chart(fig_line, use_container_width=True)

    except Exception as e:
        st.error(f"Execution Error loading cohort metrics: {e}")


# Regional Chapter Performance Metrics
with tab2:
    st.subheader("Cross-Sectional Chapter Performance Metrics")
    st.markdown("Operational accountability tracking across distributed geographic chapters.")
    
    try:
        df_chapters = pd.read_sql("SELECT * FROM view_chapter_performance;", con=engine)
        
        if df_chapters.empty:
            st.info("Views successfully loaded, but no matching activity logs exist yet. Showing skeleton metrics framework.")
            
            # Graceful skeleton container fallback so layout never feels broken or completely empty
            col1, col2, col3 = st.columns(3)
            col1.metric("Active Chapters", "0", delta="Awaiting Ingestion")
            col2.metric("System-Wide Engagement", "0.0 / 10")
            col3.metric("Identified At-Risk Users", "0")
        else:
            # Executive Dashboard KPI Scorecards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Active Chapters", len(df_chapters["chapter_id"].unique()))
            with col2:
                st.metric("Avg Hours Worked / Event", f"{df_chapters['avg_hours_per_event'].mean():.1f} hrs")
            with col3:
                st.metric("Mean System Engagement", f"{df_chapters['avg_engagement_score'].mean():.2f} / 10")
            with col4:
                st.metric("Aggregated Churn Volume", int(df_chapters["churned_count"].sum()), delta="Action Required", delta_color="inverse")
            
            st.markdown("---")
            
            # Strategic Performance Grouping
            st.markdown("### Operational Risk Distribution Matrix")
            fig_bar = px.bar(
                df_chapters,
                x="chapter_id",
                y="churned_count",
                color="region",
                title="Total Churned Volunteers by Unique Chapter ID (Flagging Regional Anomalies)",
                labels={"chapter_id": "Chapter Code Identifier", "churned_count": "Inactive Users (>60 Days)"},
                text_auto=True
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Interactive Data Review Interface
            st.markdown("### Chapter Performance Leaderboard")
            st.dataframe(
                df_chapters.sort_values(by="churned_count", ascending=False),
                use_container_width=True,
                hide_index=True
            )
                
    except Exception as e:
        st.error(f"Execution Error loading operational metrics: {e}")