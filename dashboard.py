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
# 2. HELPER FUNCTIONS
# ==========================================

@st.cache_data(ttl=10)
def fetch_data(endpoint):
    response = requests.get(
        f"{API_URL}/{endpoint}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def download_csv(dataframe, filename, label):
    if not dataframe.empty:
        csv_data = dataframe.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=label,
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            key=filename
        )
    else:
        st.info("No data available to export.")


def get_boolean_series(series):
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )


# ==========================================
# 3. DASHBOARD HEADER
# ==========================================

st.title("🧠 CogniStream")
st.subheader("Developer Flow-State & Cognitive Load Analytics")
st.markdown("---")


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
    flow_data = fetch_data("flow-sessions")

    developer_df = pd.DataFrame(developers)
    event_df = pd.DataFrame(events)

    activity_df = pd.DataFrame(
        activity.get("events", [])
    )

    cognitive_df = pd.DataFrame(
        cognitive_data.get("cognitive_load", [])
    )

    flow_df = pd.DataFrame(
        flow_data.get("flow_sessions", [])
    )

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
            .astype(str)
            .tolist()
        )

        selected_developer = st.selectbox(
            "Select Developer",
            developer_list
        )

    else:
        selected_developer = "All Developers"

    if selected_developer != "All Developers":

        filtered_developer_df = developer_df[
            developer_df["developer_id"] == selected_developer
        ].copy()

        if "developer_id" in activity_df.columns:
            filtered_activity_df = activity_df[
                activity_df["developer_id"] == selected_developer
            ].copy()
        else:
            filtered_activity_df = activity_df.copy()

    else:
        filtered_developer_df = developer_df.copy()
        filtered_activity_df = activity_df.copy()

    # ======================================
    # 6. KPI METRICS
    # ======================================

    total_events = len(activity_df)
    total_developers = len(developer_df)

    if (
        not activity_df.empty
        and "event_type" in activity_df.columns
    ):
        total_event_types = activity_df["event_type"].nunique()
    else:
        total_event_types = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Events", total_events)
    col2.metric("Total Developers", total_developers)
    col3.metric("Event Categories", total_event_types)

    st.markdown("---")

    # ======================================
    # 7. DEVELOPER ACTIVITY
    # ======================================

    st.subheader("👨‍💻 Developer Activity")

    if (
        not filtered_developer_df.empty
        and "total_events" in filtered_developer_df.columns
    ):

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

        download_csv(
            filtered_activity_df,
            "cognistream_activity_report.csv",
            "📥 Download Activity Report"
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

        if selected_developer != "All Developers":
            filtered_cognitive_df = cognitive_df[
                cognitive_df["developer_id"] == selected_developer
            ].copy()

        required_cognitive_columns = [
            "developer_id",
            "focus_percentage",
            "interruption_percentage"
        ]

        if all(
            col in filtered_cognitive_df.columns
            for col in required_cognitive_columns
        ) and not filtered_cognitive_df.empty:

            filtered_cognitive_df["focus_percentage"] = pd.to_numeric(
                filtered_cognitive_df["focus_percentage"],
                errors="coerce"
            )

            filtered_cognitive_df["interruption_percentage"] = pd.to_numeric(
                filtered_cognitive_df["interruption_percentage"],
                errors="coerce"
            )

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

            st.subheader("🎯 Focus Percentage by Developer")

            fig3 = px.bar(
                filtered_cognitive_df,
                x="developer_id",
                y="focus_percentage",
                color="developer_id",
                title="Developer Focus Performance",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

            st.subheader("⚡ Interruption Percentage by Developer")

            fig4 = px.bar(
                filtered_cognitive_df,
                x="developer_id",
                y="interruption_percentage",
                color="developer_id",
                title="Developer Interruption Analysis",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

            st.subheader("📊 Cognitive Load Summary")

            st.dataframe(
                filtered_cognitive_df,
                use_container_width=True,
                hide_index=True
            )

            download_csv(
                filtered_cognitive_df,
                "cognistream_cognitive_load_report.csv",
                "📥 Download Cognitive Load Report"
            )

        else:
            st.info("Required cognitive-load columns or records are missing.")

    else:
        st.warning("Cognitive load data is not available.")

    # ======================================
    # 11. FLOW-STATE ANALYTICS
    # ======================================

    st.markdown("---")
    st.subheader("🚀 Flow-State Analytics")

    if not flow_df.empty:

        filtered_flow_df = flow_df.copy()

        if selected_developer != "All Developers":
            filtered_flow_df = flow_df[
                flow_df["developer_id"] == selected_developer
            ].copy()

        if (
            not filtered_flow_df.empty
            and "duration_minutes" in filtered_flow_df.columns
        ):

            filtered_flow_df["duration_minutes"] = pd.to_numeric(
                filtered_flow_df["duration_minutes"],
                errors="coerce"
            )

            valid_sessions = filtered_flow_df.dropna(
                subset=["duration_minutes"]
            ).copy()

            if not valid_sessions.empty:

                if "qualified_90_min" in valid_sessions.columns:
                    deep_focus_mask = get_boolean_series(
                        valid_sessions["qualified_90_min"]
                    )
                else:
                    deep_focus_mask = pd.Series(
                        False,
                        index=valid_sessions.index
                    )

                total_sessions = len(valid_sessions)

                avg_duration = valid_sessions[
                    "duration_minutes"
                ].mean()

                longest_session = valid_sessions[
                    "duration_minutes"
                ].max()

                deep_focus_sessions = int(deep_focus_mask.sum())

                developers_with_sessions = (
                    valid_sessions["developer_id"].nunique()
                    if "developer_id" in valid_sessions.columns
                    else 0
                )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total Focus Sessions", total_sessions)

                col2.metric(
                    "Average Session Duration",
                    f"{avg_duration:.2f} min"
                )

                col3.metric(
                    "Longest Focus Session",
                    f"{longest_session:.2f} min"
                )

                col4.metric(
                    "Deep-Focus Sessions (90+ min)",
                    deep_focus_sessions
                )

                st.metric(
                    "Developers with Sessions",
                    developers_with_sessions
                )

                if "developer_id" in valid_sessions.columns:

                    st.subheader(
                        "⏱️ Average Focus Duration by Developer"
                    )

                    developer_duration = (
                        valid_sessions
                        .groupby("developer_id")["duration_minutes"]
                        .mean()
                        .reset_index()
                    )

                    fig5 = px.bar(
                        developer_duration,
                        x="developer_id",
                        y="duration_minutes",
                        color="developer_id",
                        title="Average Focus Session Duration",
                        labels={
                            "developer_id": "Developer",
                            "duration_minutes": "Average Duration (Minutes)"
                        },
                        template="plotly_dark"
                    )

                    st.plotly_chart(
                        fig5,
                        use_container_width=True
                    )

                st.subheader("🧠 Deep-Focus Session Records")

                deep_focus_df = valid_sessions[
                    deep_focus_mask
                ]

                if not deep_focus_df.empty:

                    st.dataframe(
                        deep_focus_df,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info(
                        "No sessions have reached the 90-minute threshold yet."
                    )

                st.subheader("📋 All Flow-State Session Records")

                st.dataframe(
                    valid_sessions,
                    use_container_width=True,
                    hide_index=True
                )

                download_csv(
                    valid_sessions,
                    "cognistream_flow_sessions_report.csv",
                    "📥 Download Flow-State Report"
                )

            else:
                st.warning("No valid session duration data available.")

        else:
            st.info("No valid flow-session records available.")

    else:
        st.warning("Flow-state session data is not available.")

    # ======================================
    # 12. DEVELOPER PRODUCTIVITY RANKING
    # ======================================

    st.markdown("---")
    st.subheader("🏆 Developer Productivity Ranking")

    productivity_df = pd.DataFrame()

    required_cognitive = [
        "developer_id",
        "focus_percentage",
        "interruption_percentage"
    ]

    required_developer = [
        "developer_id",
        "total_events"
    ]

    required_flow = [
        "developer_id",
        "qualified_90_min"
    ]

    if (
        not cognitive_df.empty
        and not developer_df.empty
        and not flow_df.empty
        and all(col in cognitive_df.columns for col in required_cognitive)
        and all(col in developer_df.columns for col in required_developer)
        and all(col in flow_df.columns for col in required_flow)
    ):

        productivity_df = cognitive_df[
            required_cognitive
        ].copy()

        productivity_df = productivity_df.merge(
            developer_df[required_developer],
            on="developer_id",
            how="left"
        )

        flow_copy = flow_df.copy()

        flow_copy["qualified_90_min"] = get_boolean_series(
            flow_copy["qualified_90_min"]
        )

        deep_focus = (
            flow_copy.groupby("developer_id")["qualified_90_min"]
            .sum()
            .reset_index(name="deep_focus_sessions")
        )

        productivity_df = productivity_df.merge(
            deep_focus,
            on="developer_id",
            how="left"
        )

        productivity_df["deep_focus_sessions"] = (
            productivity_df["deep_focus_sessions"].fillna(0)
        )

        for column in [
            "total_events",
            "focus_percentage",
            "interruption_percentage"
        ]:

            productivity_df[column] = pd.to_numeric(
                productivity_df[column],
                errors="coerce"
            ).fillna(0)

        productivity_df["focus_score"] = (
            productivity_df["focus_percentage"].clip(0, 100)
        )

        max_deep_focus = productivity_df[
            "deep_focus_sessions"
        ].max()

        max_events = productivity_df[
            "total_events"
        ].max()

        if max_deep_focus > 0:

            productivity_df["deep_focus_score"] = (
                productivity_df["deep_focus_sessions"]
                / max_deep_focus * 100
            )

        else:
            productivity_df["deep_focus_score"] = 0

        if max_events > 0:

            productivity_df["activity_score"] = (
                productivity_df["total_events"]
                / max_events * 100
            )

        else:
            productivity_df["activity_score"] = 0

        productivity_df["low_interruption_score"] = (
            100 - productivity_df[
                "interruption_percentage"
            ].clip(0, 100)
        )

        productivity_df["productivity_score"] = (
            productivity_df["focus_score"] * 0.40
            + productivity_df["deep_focus_score"] * 0.30
            + productivity_df["activity_score"] * 0.20
            + productivity_df["low_interruption_score"] * 0.10
        )

        productivity_df = productivity_df.sort_values(
            "productivity_score",
            ascending=False
        ).reset_index(drop=True)

        productivity_df.insert(
            0,
            "rank",
            range(1, len(productivity_df) + 1)
        )

        if selected_developer != "All Developers":

            display_productivity_df = productivity_df[
                productivity_df["developer_id"] == selected_developer
            ].copy()

        else:
            display_productivity_df = productivity_df.copy()

        st.subheader("🥇 Developer Leaderboard")

        leaderboard_columns = [
            "rank",
            "developer_id",
            "productivity_score",
            "focus_percentage",
            "deep_focus_sessions",
            "total_events",
            "interruption_percentage"
        ]

        st.dataframe(
            display_productivity_df[
                leaderboard_columns
            ].round(2),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📊 Productivity Score Comparison")

        if not display_productivity_df.empty:

            fig6 = px.bar(
                display_productivity_df,
                x="developer_id",
                y="productivity_score",
                color="developer_id",
                title="Developer Productivity Score",
                labels={
                    "developer_id": "Developer",
                    "productivity_score": "Productivity Score"
                },
                template="plotly_dark"
            )

            fig6.update_traces(
                texttemplate="%{y:.2f}",
                textposition="outside"
            )

            st.plotly_chart(
                fig6,
                use_container_width=True
            )

        st.caption(
            "Illustrative score: Focus 40% + Deep Focus 30% "
            "+ Activity 20% + Low Interruptions 10%. "
            "This ranking uses synthetic activity data and "
            "does not directly measure actual productivity."
        )

        st.subheader("📥 Download Productivity Report")

        download_csv(
            productivity_df,
            "cognistream_productivity_report.csv",
            "Download Full Productivity Ranking (CSV)"
        )

    else:
        st.warning(
            "Productivity ranking requires valid developer, "
            "cognitive-load and flow-session data."
        )

    # ======================================
    # 13. PROJECT SUMMARY & KEY INSIGHTS
    # ======================================

    st.markdown("---")
    st.header("📌 Project Summary & Key Insights")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    summary_col1.metric(
        "Developers Analysed",
        len(developer_df)
    )

    if "total_events" in developer_df.columns:

        summary_total_events = pd.to_numeric(
            developer_df["total_events"],
            errors="coerce"
        ).fillna(0).sum()

    else:
        summary_total_events = 0

    summary_col2.metric(
        "Total Activity Events",
        int(summary_total_events)
    )

    if (
        not flow_df.empty
        and "qualified_90_min" in flow_df.columns
    ):

        summary_deep_focus = int(
            get_boolean_series(
                flow_df["qualified_90_min"]
            ).sum()
        )

    else:
        summary_deep_focus = 0

    summary_col3.metric(
        "Deep-Focus Sessions",
        summary_deep_focus
    )

    if not productivity_df.empty:

        top_developer = productivity_df.iloc[0]

        st.subheader("🏆 Top-Ranked Developer")

        st.success(
            f"{top_developer['developer_id']} | "
            f"Illustrative Score: "
            f"{top_developer['productivity_score']:.2f}/100"
        )

        st.subheader("💡 Key Insights")

        st.write(
            f"- {len(developer_df)} developers were analysed."
        )

        st.write(
            f"- {int(summary_total_events)} activity events were recorded."
        )

        st.write(
            f"- {summary_deep_focus} sessions reached 90 minutes or more."
        )

        st.write(
            f"- {top_developer['developer_id']} achieved the highest illustrative productivity score."
        )

    else:
        st.info(
            "Productivity insights will appear when all required analytics data is available."
        )

    st.caption(
        "Insights are based on synthetic activity data. "
        "They are not a direct measurement of actual developer productivity."
    )

    # ======================================
    # 14. FOOTER
    # ======================================

    st.markdown("---")

    st.caption("CogniStream | Developer Analytics Platform")

    st.caption(
        "Focus and interruption percentages are event-based indicators, "
        "not direct measurements of mental workload. "
        "Flow sessions are estimated from activity events. "
        "Deep focus is defined as a session lasting 90 minutes or more."
    )


# ==========================================
# 15. ERROR HANDLING
# ==========================================

except requests.exceptions.ConnectionError:

    st.error(
        "Cannot connect to FastAPI. "
        "Please start the backend on port 8000."
    )

except requests.exceptions.Timeout:

    st.error(
        "The API request timed out. "
        "Please check whether FastAPI is responding."
    )

except requests.exceptions.RequestException as error:

    st.error(f"API request failed: {error}")

except Exception as error:

    st.error(f"Dashboard error: {error}")