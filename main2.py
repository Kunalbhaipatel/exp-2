# full_fixed_dashboard.py
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Rig Comparison Dashboard", layout="wide")
st.title("🚀 Rig Comparison Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("Updated_Merged_Data_with_API_and_Location.csv")
    if "Efficiency Score" in df.columns and df["Efficiency Score"].isnull().all():
        df.drop(columns=["Efficiency Score"], inplace=True)
    return df

data = load_data()
filtered = data.copy()

with st.container():
    col_search, col1, col2, col3, col4 = st.columns([2.5, 1.2, 1.2, 1.2, 1.2])
    with col_search:
        st.markdown("🔍 **Global Search**")
        search_term = st.text_input("Search any column...")
        if search_term:
            search_term = search_term.lower()
            filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)]
            st.success(f"🔎 Found {len(filtered)} matching rows.")
    with col1:
        selected_operator = st.selectbox("Operator", ["All"] + sorted(data["Operator"].dropna().unique().tolist()))
        if selected_operator != "All":
            filtered = filtered[filtered["Operator"] == selected_operator]
    with col2:
        selected_contractor = st.selectbox("Contractor", ["All"] + sorted(data["Contractor"].dropna().unique().tolist()))
        if selected_contractor != "All":
            filtered = filtered[filtered["Contractor"] == selected_contractor]
    with col3:
        if "flowline_Shakers" in data.columns:
            selected_shaker = st.selectbox("Shaker", ["All"] + sorted(data["flowline_Shakers"].dropna().unique().tolist()))
            if selected_shaker != "All":
                filtered = filtered[filtered["flowline_Shakers"] == selected_shaker]
        else:
            st.warning("⚠️ 'flowline_Shakers' column not found in dataset.")
    with col4:
        if "Hole_Size" in data.columns:
            selected_hole = st.selectbox("Hole Size", ["All"] + sorted(data["Hole_Size"].dropna().unique().tolist()))
            if selected_hole != "All":
                filtered = filtered[filtered["Hole_Size"] == selected_hole]

st.markdown("### 📊 Key Metrics")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Avg Total Dilution", f"{filtered['Total_Dil'].mean():,.2f} BBLs")
with m2:
    st.metric("Avg SCE", f"{filtered['Total_SCE'].mean():,.2f}")
with m3:
    st.metric("Avg DSRE", f"{filtered['DSRE'].mean()*100:.1f}%")

# Tabs
st.markdown("## 🧭 Dashboard Sections")
tabs = st.tabs([
    "🧾 Well Overview",
    "📋 Summary & Charts",
    "📊 Statistical Insights",
    "📈 Advanced Analytics",
    "🧮 Derrick Comparison",
    "⚙️ Advanced Filters"
])

with tabs[0]:
    st.subheader("📄 Well Overview")
    selected_metric = st.selectbox("Choose a metric to visualize", ["Total_Dil", "Total_SCE", "DSRE"])
    if "Well_Name" in filtered.columns and selected_metric in filtered.columns:
        metric_data = filtered[["Well_Name", selected_metric]].dropna()
        metric_data = metric_data.groupby("Well_Name")[selected_metric].mean().reset_index()
        metric_data.rename(columns={selected_metric: "Value"}, inplace=True)
        fig = px.bar(metric_data, x="Well_Name", y="Value", title=f"Well Name vs {selected_metric}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Required columns not found.")

with tabs[1]:
    st.subheader("📋 Summary & Charts")
    subset = filtered.dropna(subset=["Well_Name"])
    y_cols = [col for col in ["Depth", "DOW"] if col in subset.columns]
    if y_cols:
        fig1 = px.bar(subset, x="Well_Name", y=y_cols, barmode='group', height=400,
                     labels={"value": "Barrels", "variable": "Metric"},
                     color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig1, use_container_width=True)
    y_cols2 = [col for col in ["Base_Oil", "Water", "Weight_Material", "Chemicals"] if col in subset.columns]
    if y_cols2:
        fig2 = px.bar(subset, x="Well_Name", y=y_cols2, barmode="stack", height=400,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

with tabs[2]:
    st.subheader("📊 Statistical Summary & Insights")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("📈 Mean DSRE", f"{filtered['DSRE'].mean()*100:.2f}%")
    with k2:
        st.metric("🚛 Max Haul Off", f"{filtered['Haul_OFF'].max():,.0f}")
    with k3:
        st.metric("🧪 Avg SCE", f"{filtered['Total_SCE'].mean():,.2f}")
    with k4:
        st.metric("💧 Avg Dilution", f"{filtered['Total_Dil'].mean():,.2f}")
    k5, k6, k7, k8 = st.columns(4)
    with k5:
        max_depth = filtered['Depth'].max() if "Depth" in filtered.columns else None
        st.metric("⛏️ Max Depth", f"{max_depth:,.0f}" if pd.notnull(max_depth) else "N/A")
    with k6:
        avg_lgs = filtered["Average_LGS%"].mean() if "Average_LGS%" in filtered.columns else None
        st.metric("🌀 Avg LGS%", f"{avg_lgs:.2f}" if pd.notnull(avg_lgs) else "N/A")
    with k7:
        avg_dil = filtered["Dilution_Ratio"].mean() if "Dilution_Ratio" in filtered.columns else None
        dil_icon = "🟢" if avg_dil < 1 else "🟡" if avg_dil < 2 else "🔴"
        st.metric("🥄 Dilution Ratio", f"{avg_dil:.2f} {dil_icon}" if avg_dil else "N/A")
    with k8:
        avg_disc = filtered["Discard Ratio"].mean() if "Discard Ratio" in filtered.columns else None
        disc_icon = "🟢" if avg_disc < 0.1 else "🟡" if avg_disc < 0.2 else "🔴"
        st.metric("🗑️ Discard Ratio", f"{avg_disc:.2f} {disc_icon}" if avg_disc else "N/A")
    st.markdown("#### 🔍 Automatic Insights")
    if 'DSRE' in filtered.columns:
        high_eff = filtered[filtered['DSRE'] > 0.9]
        low_eff = filtered[filtered['DSRE'] < 0.6]
        st.success(f"✅ **High Efficiency Wells (DSRE > 90%)**: {len(high_eff)}")
        st.warning(f"⚠️ **Low Efficiency Wells (DSRE < 60%)**: {len(low_eff)}")

with tabs[3]:
    st.subheader("📈 Advanced Analytics")
    if "ROP" in filtered.columns and "Temp" in filtered.columns:
        fig = px.scatter(filtered, x="ROP", y="Temp", color="Well_Name", title="ROP vs Temperature")
        st.plotly_chart(fig, use_container_width=True)

with tabs[4]:
    st.subheader("🧮 Derrick vs Non-Derrick Comparison")
    if "flowline_Shakers" in filtered.columns:
        filtered["Shaker_Type"] = filtered["flowline_Shakers"].apply(
            lambda x: "Derrick" if isinstance(x, str) and "derrick" in x.lower() else "Non-Derrick")
        selected_metrics = st.multiselect("📌 Select Metrics to Compare", [
            "DSRE", "Discard Ratio", "Total_SCE", "Total_Dil", "ROP", "Temp",
            "DOW", "AMW", "Drilling_Hours", "Haul_OFF", "Base_Oil", "Water",
            "Weight_Material", "Chemicals", "Dilution_Ratio", "Solids_Generated"
        ], default=["DSRE", "ROP", "Total_Dil"])
        if selected_metrics:
            derrick_avg = filtered[filtered["Shaker_Type"] == "Derrick"][selected_metrics].mean().reset_index()
            derrick_avg.columns = ["Metric", "Derrick"]
            non_derrick_avg = filtered[filtered["Shaker_Type"] == "Non-Derrick"][selected_metrics].mean().reset_index()
            non_derrick_avg.columns = ["Metric", "Non-Derrick"]
            merged = pd.merge(derrick_avg, non_derrick_avg, on="Metric")
            melted = pd.melt(merged, id_vars="Metric", value_vars=["Derrick", "Non-Derrick"],
                             var_name="Shaker_Type", value_name="Average")
            fig = px.bar(melted, x="Metric", y="Average", color="Shaker_Type",
                         color_discrete_map={"Derrick": "#007535", "Non-Derrick": "gray"},
                         barmode="group", title="📊 Average Metrics: Derrick vs Non-Derrick")
            st.plotly_chart(fig, use_container_width=True)
            if "DSRE" in filtered.columns:
                filtered["Efficiency Score"] = (
                    filtered["DSRE"].fillna(0)*100 -
                    filtered.get("Dilution_Ratio", 0).fillna(0)*10 -
                    filtered.get("Discard Ratio", 0).fillna(0)*10)
                filtered["Flag"] = filtered["Shaker_Type"].map({"Derrick": "🟩 Derrick", "Non-Derrick": "🟥 Non-Derrick"})
                rank_df = filtered[["Well_Name", "Shaker_Type", "Efficiency Score", "Flag"]].sort_values(
                    by="Efficiency Score", ascending=False).reset_index(drop=True)
                st.markdown("### 🏅 Ranked Wells by Efficiency Score")
                st.dataframe(rank_df.drop(columns=["Shaker_Type"]), use_container_width=True)

with tabs[5]:
    st.subheader("⚙️ Advanced Filters")
    if "TD_Date" in data.columns:
        data["TD_Date"] = pd.to_datetime(data["TD_Date"], errors='coerce')
        data["TD_Year"] = data["TD_Date"].dt.year
        selected_year = st.selectbox("Select Year", ["All"] + sorted(data["TD_Year"].dropna().unique().astype(str)))
        if selected_year != "All":
            filtered = filtered[filtered["TD_Year"] == int(selected_year)]
    st.dataframe(filtered)

st.markdown("""
<div style='position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1c1c1c; color: white; text-align: center; padding: 8px 0; font-size: 0.9rem; z-index: 999;'>
    &copy; 2025 Derrick Corp | Designed for drilling performance insights
</div>
""", unsafe_allow_html=True)
