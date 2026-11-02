
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CogniStream Analytics",
    page_icon="🧠",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"

# ==========================================
# 2. DASHBOARD HEADER
# ==========================================

st.title("🧠 CogniStream")
st.subheader("Developer Flow-State & Cognitive Load Analytics")

st.markdown("---")

# ==========================================
# 3. API DATA FETCHING
# ==========================================

@st.cache_data(ttl=10)
def fetch_data(endpoint):
    response = requests.get(
        f"{API_URL}/{endpoint}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


# ==========================================
# 4. LOAD DATA
# ==========================================

try:

    if st.button("🔄 Refresh Dashboard"):
        st.cache_data.clear()
        st.rerun()

    developers = fetch_data("developers")
    events = fetch_data("event-summary")
    activity = fetch_data("activity")
    cognitive_data = fetch_data("cognitive-load")

    # Convert API responses into DataFrames

    developer_df = pd.DataFrame(developers)
    event_df = pd.DataFrame(events)

    activity_records = activity.get("events", [])
    activity_df = pd.DataFrame(activity_records)

    cognitive_records = cognitive_data.get(
        "cognitive_load", []
    )
    cognitive_df = pd.DataFrame(cognitive_records)

    # ======================================
    # 5. DEVELOPER FILTER
    # ======================================

    st.subheader("🔎 Developer Filter")

    if (
        not developer_df.empty
        and "developer_id" in developer_df.columns
    ):

        developer_list = (
            ["All Developers"]
            + developer_df["developer_id"]
            .dropna()
            .tolist()
        )

        selected_developer = st.selectbox(
            "Select Developer",
            developer_list
        )

        if selected_developer != "All Developers":

            filtered_developer_df = developer_df[
                developer_df["developer_id"]
                == selected_developer
            ]

            filtered_activity_df = activity_df[
                activity_df["developer_id"]
                == selected_developer
            ] if "developer_id" in activity_df.columns else activity_df.copy()

        else:

            filtered_developer_df = developer_df.copy()
            filtered_activity_df = activity_df.copy()

    else:

        selected_developer = "All Developers"
        filtered_developer_df = developer_df.copy()
        filtered_activity_df = activity_df.copy()

    # ======================================
    # 6. KPI METRICS
    # ======================================

    total_events = (
        len(filtered_activity_df)
        if not filtered_activity_df.empty
        else 0
    )

    total_developers = len(filtered_developer_df)

    total_event_types = (
        filtered_activity_df["event_type"].nunique()
        if "event_type" in filtered_activity_df.columns
        else len(event_df)
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Events", total_events)
    col2.metric("Total Developers", total_developers)
    col3.metric("Event Categories", total_event_types)

    st.markdown("---")

    # ======================================
    # 7. DEVELOPER ACTIVITY
    # ======================================

    st.subheader("👨‍💻 Developer Activity")

    if not filtered_developer_df.empty:

        fig1 = px.bar(
            filtered_developer_df,
            x="developer_id",
            y="total_events",
            color="developer_id",
            title="Events by Developer",
            labels={
                "developer_id": "Developer",
                "total_events": "Total Events"
            },
            template="plotly_dark"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:
        st.info("No developer data available.")

    # ======================================
    # 8. EVENT DISTRIBUTION
    # ======================================

    st.subheader("📊 Event Distribution")

    if (
        not filtered_activity_df.empty
        and "event_type" in filtered_activity_df.columns
    ):

        event_distribution = (
            filtered_activity_df["event_type"]
            .value_counts()
            .reset_index()
        )

        event_distribution.columns = [
            "event_type",
            "total_events"
        ]

        fig2 = px.pie(
            event_distribution,
            names="event_type",
            values="total_events",
            hole=0.45,
            title="Distribution of Event Types",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:
        st.info("No event data available.")

    # ======================================
    # 9. RECENT DEVELOPER ACTIVITY
    # ======================================

    st.subheader("📋 Recent Developer Activity")

    if not filtered_activity_df.empty:

        st.dataframe(
            filtered_activity_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No activity records available.")

    # ======================================
    # 10. COGNITIVE LOAD ANALYSIS
    # ======================================

    st.markdown("---")

    st.subheader("🧠 Cognitive Load Analysis")

    if not cognitive_df.empty:

        filtered_cognitive_df = cognitive_df.copy()

        if (
            selected_developer != "All Developers"
            and "developer_id" in cognitive_df.columns
        ):

            filtered_cognitive_df = cognitive_df[
                cognitive_df["developer_id"]
                == selected_developer
            ]

        if not filtered_cognitive_df.empty:

            # Focus and interruption metrics

            focus_avg = filtered_cognitive_df[
                "focus_percentage"
            ].mean()

            interruption_avg = filtered_cognitive_df[
                "interruption_percentage"
            ].mean()

            col1, col2 = st.columns(2)

            col1.metric(
                "Average Focus",
                f"{focus_avg:.2f}%"
            )

            col2.metric(
                "Average Interruptions",
                f"{interruption_avg:.2f}%"
            )

            # Focus percentage chart

            st.subheader("🎯 Focus Percentage by Developer")

            fig3 = px.bar(
                filtered_cognitive_df,
                x="developer_id",
                y="focus_percentage",
                color="developer_id",
                title="Developer Focus Performance",
                labels={
                    "developer_id": "Developer",
                    "focus_percentage": "Focus Percentage"
                },
                template="plotly_dark"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

            # Interruption percentage chart

            st.subheader("⚡ Interruption Percentage by Developer")

            fig4 = px.bar(
                filtered_cognitive_df,
                x="developer_id",
                y="interruption_percentage",
                color="developer_id",
                title="Developer Interruption Analysis",
                labels={
                    "developer_id": "Developer",
                    "interruption_percentage": "Interruption Percentage"
                },
                template="plotly_dark"
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

            # Cognitive load summary table

            st.subheader("📊 Cognitive Load Summary")

            st.dataframe(
                filtered_cognitive_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No cognitive load data for this developer.")

    else:
        st.warning("Cognitive load data is not available.")

    # ======================================
    # 11. FOOTER
    # ======================================

    st.markdown("---")

    st.caption(
        "CogniStream | Developer Analytics Platform"
    )

    st.caption(
        "Note: Focus and interruption percentages are "
        "event-based indicators, not direct measurements "
        "of a developer's mental state."
    )

except requests.exceptions.ConnectionError:

    st.error(
        "Cannot connect to FastAPI. "
        "Please start the backend on port 8000."
    )

except requests.exceptions.RequestException as error:

    st.error(f"API request failed: {error}")

except Exception as error:

    st.error(f"Dashboard error: {error}")
