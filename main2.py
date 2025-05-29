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

tabs = st.tabs(["Well Overview", "Summary & Charts", "Statistical Insights", "Advanced Analytics", "Derrick Comparison", "Advanced Filters"])

with tabs[0]:
    st.subheader("📄 Well Overview")
    st.markdown("Analyze well-level performance metrics as grouped column bar charts.")
    selected_metric = st.selectbox("Choose a metric to visualize", ["Total_Dil", "Total_SCE", "DSRE"])
    if "Well_Name" in filtered.columns and selected_metric in filtered.columns:
        metric_data = filtered[["Well_Name", selected_metric]].dropna()
        metric_data = metric_data.groupby("Well_Name")[selected_metric].mean().reset_index()
        metric_data.rename(columns={selected_metric: "Value"}, inplace=True)
        fig = px.bar(metric_data, x="Well_Name", y="Value", title=f"Well Name vs {selected_metric}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Required columns not found.")

# ---------- MAIN TABS ----------
tabs = st.tabs([
    "🧾 Well Overview", 
    "📋 Summary & Charts", 
    "📊 Statistical Insights", 
    "📈 Advanced Analytics", 
    "🧮 Multi-Well Comparison", 
    "⚙️ Advanced Tab"
])

# ---------- ADVANCED FILTERS TAB ----------
with tabs[5]:
    st.markdown("### ⚙️ Advanced Filters")
    st.info("Use sliders and dropdowns to drill down on performance.")

    col1, col2 = st.columns(2)
    with col1:
        if "IntLength" in data.columns:
            min_val, max_val = int(data["IntLength"].min()), int(data["IntLength"].max())
            int_range = st.slider("Interval Length", min_val, max_val, (min_val, max_val))
            filtered = filtered[(filtered["IntLength"] >= int_range[0]) & (filtered["IntLength"] <= int_range[1])]
        if "AMW" in data.columns:
            min_amw, max_amw = float(data["AMW"].min()), float(data["AMW"].max())
            amw_range = st.slider("Average Mud Weight (AMW)", min_amw, max_amw, (min_amw, max_amw))
            filtered = filtered[(filtered["AMW"] >= amw_range[0]) & (filtered["AMW"] <= amw_range[1])]

    with col2:
        if "Average_LGS%" in data.columns:
            lgs_min, lgs_max = float(data["Average_LGS%"].min()), float(data["Average_LGS%"].max())
            lgs_range = st.slider("Average LGS%", lgs_min, lgs_max, (lgs_min, lgs_max))
            filtered = filtered[(filtered["Average_LGS%"] >= lgs_range[0]) & (filtered["Average_LGS%"] <= lgs_range[1])]

        if "TD_Date" in data.columns and not data["TD_Date"].isnull().all():
            try:
                data["TD_Date"] = pd.to_datetime(data["TD_Date"], errors='coerce')
                data["TD_Year"] = data["TD_Date"].dt.year
                data["TD_Month"] = data["TD_Date"].dt.strftime('%B')

                td_years = sorted(data["TD_Year"].dropna().unique())
                td_months = ["January", "February", "March", "April", "May", "June",
                             "July", "August", "September", "October", "November", "December"]

                selected_year = st.selectbox("Select TD Year", options=["All"] + [int(y) for y in td_years])
                selected_month = st.selectbox("Select TD Month", options=["All"] + td_months)

                if selected_year != "All":
                    filtered = filtered[filtered["TD_Year"] == selected_year]
                if selected_month != "All":
                    filtered = filtered[filtered["TD_Month"] == selected_month]
            except Exception as e:
                st.warning(f"⚠️ TD_Date processing failed: {e}")

    st.markdown("### 🔍 Filtered Results Preview")
    st.dataframe(filtered)

# ---------- FOOTER ----------
st.markdown("""
<div style='position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1c1c1c; color: white; text-align: center; padding: 8px 0; font-size: 0.9rem; z-index: 999;'>
    &copy; 2025 Derrick Corp | Designed for drilling performance insights
</div>
""", unsafe_allow_html=True)

# ---------- TAB 1: WELL OVERVIEW ----------
with tabs[0]:
    st.subheader("📄 Well Overview")
    st.markdown("Analyze well-level performance metrics as grouped column bar charts.")

    selected_metric = st.selectbox("Choose a metric to visualize", ["Total_Dil", "Total_SCE", "DSRE"])

    # Prepare data for visualization
    metric_data = filtered[["Well_Name", selected_metric]].dropna()
    metric_data = metric_data.groupby("Well_Name")[selected_metric].mean().reset_index()
    metric_data.rename(columns={selected_metric: "Value"}, inplace=True)

    import plotly.express as px
    fig = px.bar(metric_data, x="Well_Name", y="Value", title=f"Well Name vs {selected_metric}")
    st.plotly_chart(fig, use_container_width=True)


# ---------- TAB 2: SUMMARY & CHARTS ----------
with tabs[1]:
    st.markdown("### 📌 Summary & Charts")

    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### 📌 Depth vs DOW")
        subset = filtered.dropna(subset=["Well_Name"])
        y_cols = [col for col in ["Depth", "DOW"] if col in subset.columns]
        if y_cols:
            fig1 = px.bar(subset, x="Well_Name", y=y_cols, barmode='group', height=400,
                         labels={"value": "Barrels", "variable": "Metric"},
                         color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("Required columns for Depth vs DOW not found.")

    with chart2:
        st.markdown("#### 🌈 Dilution Breakdown")
        y_cols = [col for col in ["Base_Oil", "Water", "Weight_Material", "Chemicals"] if col in subset.columns]
        if y_cols:
            fig2 = px.bar(subset, x="Well_Name", y=y_cols, barmode="stack", height=400,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Required columns for Dilution Breakdown not found.")

    st.markdown("### 📈 DSRE vs Ratios")
    if "DSRE" in subset.columns:
        try:
            fig3 = px.bar(subset, x="Well_Name", y="DSRE", height=400,
                         labels={"DSRE": "DSRE"}, color_discrete_sequence=["#66c2a5"])
            if "Discard Ratio" in subset.columns:
                fig3.add_scatter(
                    x=subset["Well_Name"],
                    y=subset["Discard Ratio"],
                    mode="lines+markers",
                    name="SCE Loss Ratio",
                    line=dict(color="red")
                )
            if "Dilution_Ratio" in subset.columns:
                fig3.add_scatter(
                    x=subset["Well_Name"],
                    y=subset["Dilution_Ratio"],
                    mode="lines+markers",
                    name="Dilution Ratio",
                    line=dict(color="gray")
                )
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.error(f"Chart rendering error: {e}")
    else:
        st.warning("DSRE column not found for chart.")

    st.markdown("### 📊 Additional Ratios Comparison")
    ratio_cols = [col for col in ["Dilution_Ratio", "Discard Ratio"] if col in subset.columns]
    if ratio_cols:
        try:
            fig4 = px.line(subset, x="Well_Name", y=ratio_cols, markers=True,
                          labels={"value": "Ratio", "variable": "Metric"},
                          title="Dilution vs SCE Loss Ratios")
            st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering ratio comparison chart: {e}")
    else:
        st.info("Dilution_Ratio and Discard Ratio columns not found for ratio comparison.")



# ---------- TAB 3: STATISTICS & INSIGHTS (ENHANCED) ----------
with tabs[2]:
    st.markdown("### 📊 Statistical Summary & Insights")

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
        if "Dilution_Ratio" in filtered.columns:
            avg_dil = filtered["Dilution_Ratio"].mean()
            dil_icon = "🟢" if avg_dil < 1 else "🟡" if avg_dil < 2 else "🔴"
            st.metric("🥄 Dilution Ratio", f"{avg_dil:.2f} {dil_icon}")
        else:
            st.metric("🥄 Dilution Ratio", "N/A")

    with k8:
        if "Discard Ratio" in filtered.columns:
            avg_disc = filtered["Discard Ratio"].mean()
            disc_icon = "🟢" if avg_disc < 0.1 else "🟡" if avg_disc < 0.2 else "🔴"
            st.metric("🗑️ Discard Ratio", f"{avg_disc:.2f} {disc_icon}")
        else:
            st.metric("🗑️ Discard Ratio", "N/A")

    # --- Insights Summary ---
    st.markdown("#### 🔍 Automatic Insights")

    if 'DSRE' in filtered.columns:
        high_eff = filtered[filtered['DSRE'] > 0.9]
        low_eff = filtered[filtered['DSRE'] < 0.6]
        st.success(f"✅ **High Efficiency Wells (DSRE > 90%)**: {len(high_eff)}")
        st.warning(f"⚠️ **Low Efficiency Wells (DSRE < 60%)**: {len(low_eff)}")
    else:
        st.info("DSRE column not found for efficiency insights.")

# ---------- TAB 4: ADVANCED ANALYTICS ----------
with tabs[3]:
    with st.expander("ℹ️ What does this section show?", expanded=False):
        st.markdown("""
### 🤖 Advanced Analytics Summary

This section helps the **drilling engineer** understand how mud composition, temperature, and drilling rate interact:

- **ROP vs Temperature**: Shows how rate of penetration changes with formation temperature. Useful for adjusting WOB or RPM.
- **Base Oil vs Water**: Indicates balance in mud systems. High water may reduce lubricity or solids suspension.
- **Correlation Heatmap**: Reveals which parameters (e.g., DSRE, dilution, discard ratio) are statistically correlated. 
  - ✅ Helps identify what to optimize (e.g., reduce dilution or increase screen performance).
  - 🛠️ Converts data into **decisions** (e.g., adjust mud ratios, optimize bit hydraulics).
""")
    st.markdown("### 🤖 Advanced Analytics & Trends")

    st.markdown("#### 📌 ROP vs Temperature")
    if "ROP" in filtered.columns and "Temp" in filtered.columns:
        try:
            fig_rop_temp = px.scatter(
                filtered, x="ROP", y="Temp", color="Well_Name",
                title="ROP vs Temperature",
                labels={"ROP": "Rate of Penetration", "Temp": "Temperature (°F)"}
            )
            st.plotly_chart(fig_rop_temp, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering ROP vs Temp chart: {e}")
    else:
        st.warning("ROP and Temp columns not found for scatter plot.")

    st.markdown("#### 📌 Base Oil vs Water Composition")
    if "Base_Oil" in filtered.columns and "Water" in filtered.columns:
        try:
            fig_bo_water = px.scatter(
                filtered, x="Base_Oil", y="Water", size="Total_Dil",
                color="Well_Name", title="Base Oil vs Water Breakdown",
                labels={"Base_Oil": "Base Oil (bbl)", "Water": "Water (bbl)"}
            )
            st.plotly_chart(fig_bo_water, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering Base Oil vs Water chart: {e}")
    else:
        st.warning("Base_Oil and Water columns not found for chart.")

    st.markdown("#### 📌 Correlation Heatmap")
    try:
        corr_cols = ["DSRE", "Total_SCE", "Total_Dil", "Discard Ratio", "Dilution_Ratio", "ROP", "AMW", "Haul_OFF"]
        corr_data = filtered[corr_cols].dropna()
        fig_corr = px.imshow(corr_data.corr(), text_auto=True, aspect="auto", color_continuous_scale='Blues')
        st.plotly_chart(fig_corr, use_container_width=True)
    except Exception as e:
        st.error(f"Correlation heatmap error: {e}")


# ---------- TAB 5: DERRICK vs NON-DERRICK ----------
with tabs[4]:
    with st.expander("ℹ️ What does this section show?", expanded=False):
        st.markdown("""
### 🧮 Derrick vs Non-Derrick Comparison

This section compares **shaker performance** across rig setups:

- **Bar Chart**: Average values of DSRE, dilution, and discard ratios across shaker types.
- **Efficiency Score**: Combines DSRE, dilution, and losses into one benchmark. Higher = more efficient solids control.
- **Practical Insight**:
  - ✅ Identify high-efficiency wells
  - 🔄 Decide if shaker replacement or screen upgrades are justified
  - 📉 Spot trends to reduce discard or dilution losses
  - 🧠 Converts data into **actions** (e.g., optimize shaker screen mesh, rebalance flowline, reduce SCE losses)
""")
    st.markdown("### 🧮 Derrick vs Non-Derrick Comparison")
    st.markdown("Compare key performance metrics by shaker type. Derrick = 🟩, Non-Derrick = 🟥")

    compare_cols = [
        "DSRE", "Discard Ratio", "Total_SCE", "Total_Dil", "ROP", "Temp", "DOW", "AMW",
        "Drilling_Hours", "Haul_OFF", "Base_Oil", "Water", "Weight_Material",
        "Chemicals", "Dilution_Ratio", "Solids_Generated"
    ]

    if "flowline_Shakers" in filtered.columns:
        filtered["Shaker_Type"] = filtered["flowline_Shakers"].apply(
            lambda x: "Derrick" if isinstance(x, str) and "derrick" in x.lower() else "Non-Derrick"
        )

        selected_metrics = st.multiselect("📌 Select Metrics to Compare", compare_cols, default=["DSRE", "ROP", "Total_Dil"])

        if selected_metrics:
            derrick_group = filtered[filtered["Shaker_Type"] == "Derrick"]
            non_derrick_group = filtered[filtered["Shaker_Type"] == "Non-Derrick"]

            derrick_avg = derrick_group[selected_metrics].mean().reset_index()
            derrick_avg.columns = ["Metric", "Derrick"]

            non_derrick_avg = non_derrick_group[selected_metrics].mean().reset_index()
            non_derrick_avg.columns = ["Metric", "Non-Derrick"]

            merged_avg = pd.merge(derrick_avg, non_derrick_avg, on="Metric")
            melted_avg = pd.melt(merged_avg, id_vars="Metric", value_vars=["Derrick", "Non-Derrick"], 
                                 var_name="Shaker_Type", value_name="Average")

            fig = px.bar(
                melted_avg, x="Metric", y="Average", color="Shaker_Type",
                color_discrete_map={"Derrick": "#007535", "Non-Derrick": "gray"},
                barmode="group", title="📊 Average Metrics: Derrick vs Non-Derrick"
            )
            st.plotly_chart(fig, use_container_width=True)

            scoring_df = filtered.copy()
            if "DSRE" in scoring_df.columns:
                scoring_df["Efficiency Score"] = (
                    scoring_df["DSRE"].fillna(0) * 100
                    - scoring_df.get("Dilution_Ratio", 0).fillna(0) * 10
                    - scoring_df.get("Discard Ratio", 0).fillna(0) * 10
                )
                scoring_df["Flag"] = scoring_df["Shaker_Type"].map({
                    "Derrick": "🟩 Derrick",
                    "Non-Derrick": "🟥 Non-Derrick"
                })
                rank_df = scoring_df[["Well_Name", "Shaker_Type", "Efficiency Score", "Flag"]]\
                    .sort_values(by="Efficiency Score", ascending=False).reset_index(drop=True)
                st.markdown("### 🏅 Ranked Wells by Efficiency Score")
                st.dataframe(rank_df.drop(columns=["Shaker_Type"]), use_container_width=True)
            else:
                st.warning("⚠️ DSRE column missing for scoring.")
        else:
            st.info("ℹ️ Please select at least one metric to compare.")
    else:
        st.warning("⚠️ 'flowline_Shakers' column not found in dataset.") "
