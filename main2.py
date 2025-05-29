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

# --- Sidebar filters and search ---
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

# --- Advanced filters ---
with st.expander("⚙️ Advanced Filters", expanded=False):
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

# --- Summary metrics ---
st.markdown("### 📊 Key Metrics")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Avg Total Dilution", f"{filtered['Total_Dil'].mean():,.2f} BBLs")
with m2:
    st.metric("Avg SCE", f"{filtered['Total_SCE'].mean():,.2f}")
with m3:
    st.metric("Avg DSRE", f"{filtered['DSRE'].mean()*100:.1f}%")

# --- Tabs and their logic ---
# [rest of the code remains unchanged here]

# --- Footer ---
st.markdown("""
<div style='position: fixed; left: 0; bottom: 0; width: 100%; background-color: #1c1c1c; color: white; text-align: center; padding: 8px 0; font-size: 0.9rem; z-index: 999;'>
    &copy; 2025 Derrick Corp | Designed for drilling performance insights
</div>
""", unsafe_allow_html=True)
