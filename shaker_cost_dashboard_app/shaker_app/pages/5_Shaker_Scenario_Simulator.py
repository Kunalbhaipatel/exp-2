
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Shaker Cost Scenario Simulator", page_icon="📐")

st.title("⚙️ Advanced Shaker Cost Simulator")

st.markdown("### Step 1: Define Cost Models")

with st.expander("🟩 Derrick Model Inputs"):
    derrick_eq = st.number_input("Derrick - Equipment Cost ($)", value=100000, key="deq")
    derrick_scr_price = st.number_input("Derrick - Screen Price ($)", value=500, key="dscr")
    derrick_scr_count = st.slider("Derrick - Screens Used", 1, 20, 4, key="dscr_cnt")
    derrick_eng = st.number_input("Derrick - Engineering/day ($)", value=1500, key="deng")
    derrick_oth = st.number_input("Derrick - Other Cost ($)", value=1000, key="doth")
    derrick_depth = st.number_input("Derrick - Total Depth/rig (ft)", value=10000, key="ddepth")

with st.expander("🟥 Non-Derrick Model Inputs"):
    nd_eq = st.number_input("Non-Derrick - Equipment Cost ($)", value=75000, key="neq")
    nd_scr_price = st.number_input("Non-Derrick - Screen Price ($)", value=400, key="nscr")
    nd_scr_count = st.slider("Non-Derrick - Screens Used", 1, 20, 4, key="nscr_cnt")
    nd_eng = st.number_input("Non-Derrick - Engineering/day ($)", value=1500, key="neng")
    nd_oth = st.number_input("Non-Derrick - Other Cost ($)", value=1000, key="noth")
    nd_depth = st.number_input("Non-Derrick - Total Depth/rig (ft)", value=10000, key="ndepth")

op_days = st.slider("Operating Days per Rig", 1, 30, 10)

st.markdown("### Step 2: Assign Model to Rig Counts")

config = {
    "3 Rigs": "Derrick",
    "5 Rigs": "Non-Derrick",
    "10 Rigs": "Derrick"
}

def calc_total_cost(rig_count, model):
    if model == "Derrick":
        scr = derrick_scr_price * derrick_scr_count * rig_count
        eq = derrick_eq * rig_count
        eng = derrick_eng * op_days * rig_count
        oth = derrick_oth * rig_count
        total = scr + eq + eng + oth
        depth = derrick_depth * rig_count
    else:
        scr = nd_scr_price * nd_scr_count * rig_count
        eq = nd_eq * rig_count
        eng = nd_eng * op_days * rig_count
        oth = nd_oth * rig_count
        total = scr + eq + eng + oth
        depth = nd_depth * rig_count

    cpf = total / depth if depth else 0
    return {
        "Rig Count": rig_count,
        "Model": model,
        "Screens": scr,
        "Equipment": eq,
        "Engineering": eng,
        "Other": oth,
        "Total": total,
        "Depth": depth,
        "Cost/Ft": cpf
    }

scenarios = [("3 Rigs", 3), ("5 Rigs", 5), ("10 Rigs", 10)]
results = [calc_total_cost(count, config[label]) for label, count in scenarios]
df = pd.DataFrame(results)

st.markdown("### 📋 Scenario Summary Table")
st.dataframe(df, use_container_width=True)

st.markdown("### 📊 Total Cost by Scenario")
fig1 = px.bar(df, x="Rig Count", y="Total", color="Model", title="Total Cost by Rig Count")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 💡 Cost Per Foot by Scenario")
fig2 = px.bar(df, x="Rig Count", y="Cost/Ft", color="Model", title="Cost per Foot by Rig Count")
st.plotly_chart(fig2, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Scenario CSV", data=csv, file_name="advanced_shaker_costs.csv", mime="text/csv")
