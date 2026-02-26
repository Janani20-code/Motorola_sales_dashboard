import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Page config
st.set_page_config(layout="wide", page_title="Motorola Executive Dashboard", initial_sidebar_state="collapsed")

# ================= GLOBAL STYLE =================
st.markdown("""
<style>
/* Background and overall layout */
.stApp { background-color: #0096EB; }
header {visibility: hidden;}
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

/* CHART BORDER + SAME SHADOW AS KPI */
[data-testid="stPlotlyChart"] {
    background-color: white !important;
    border: 2px solid black !important;
    border-radius: 15px !important;
    box-shadow: 8px 8px 15px rgba(0,0,0,0.3) !important;
    padding: 10px !important;
    margin-bottom: 25px !important;
}

/* KPI CARD STYLE */
.kpi-box {
    background-color: white !important;
    padding: 12px !important;
    border-radius: 15px !important;
    border: 2px solid black !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    box-shadow: 8px 8px 15px rgba(0,0,0,0.3) !important;
    height: 90px !important;
    margin-bottom: 15px !important;
}
.kpi-text h4 { margin: 0; font-size: 11px; color: #555; font-weight: 700; text-transform: uppercase; }
.kpi-text h2 { margin: 0; font-size: 24px; font-weight: 900; color: #111; }

/* MONTH SELECTOR */
div[data-testid="stRadio"] > div {
    flex-direction: column !important;
    gap: 8px !important;
}

div[data-testid="stRadio"] label {
    background-color: white !important;
    border: 1px solid #e6e6e6 !important;
    border-radius: 50px !important;
    padding: 8px 25px !important;
    width: 100% !important;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.2) !important;
    cursor: pointer !important;
}

div[data-testid="stRadio"] label p {
    color: #333 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    margin: 0 !important;
}

/* Hide radio circle */
div[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] ~ div { display: none !important; }
div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }

/* Selected month */
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    border: 2px solid black !important;
    background-color: #f0f0f0 !important;
}

/* Hide widget label */
[data-testid="stWidgetLabel"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ================= DATA LOADING =================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=True)
    except:
        df = pd.DataFrame({
            "order_date": pd.date_range(start="2023-01-01", periods=365),
            "revenue": [50000]*365, "sales": [100]*365, "city": ["New Delhi"]*365,
            "lat": [28.61]*365, "lon": [77.20]*365, "model": ["Moto Edge"]*365,
            "payment_method": ["UPI"]*365, "ratings": [5]*365
        })
    df["Month"] = df["order_date"].dt.month_name()
    return df

df = load_data()

month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]

# ================= HELPERS =================
def format_number(value):
    if value >= 1e3: return f"{value/1e3:.1f}K"
    return f"{value:.0f}"

def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

logos = [get_base64(f"images/logo{i}.png") for i in range(1, 5)]

TRANS_BG = "rgba(0,0,0,0)"
CHART_MARGINS = dict(l=15, r=15, t=40, b=40)

# ================= LAYOUT =================
col_nav, col_main = st.columns([0.8, 5], gap="small")

with col_nav:
    st.image("images/motorola_png.png", use_container_width=True)
    selected_month = st.radio("Month", month_order)

filtered_df = df[df["Month"] == selected_month]

with col_main:

    # ROW 1
    r1_left, r1_right = st.columns([1.6, 2.4], gap="medium")

    with r1_left:
        k_c1, k_c2 = st.columns(2)
        k_c3, k_c4 = st.columns(2)

        rev = filtered_df["revenue"].sum()
        qty = filtered_df["sales"].sum()
        trans = len(filtered_df)
        avg = rev/trans if trans > 0 else 0

        metrics = [
            ("Total Revenue", format_number(rev), logos[0], k_c1),
            ("Total Quantity", format_number(qty), logos[1], k_c2),
            ("Transactions", format_number(trans), logos[2], k_c3),
            ("Average Sales", format_number(avg), logos[3], k_c4)
        ]

        for title, val, img, col in metrics:
            col.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-text">
                    <h4>{title}</h4>
                    <h2>{val}</h2>
                </div>
                <img src="data:image/png;base64,{img}" width="38">
            </div>
            """, unsafe_allow_html=True)

    with r1_right:
        daily_sales = filtered_df.groupby(filtered_df["order_date"].dt.day)["sales"].sum().reset_index()
        fig_line = px.line(daily_sales, x="order_date", y="sales", markers=True, title="<b>Total Quantity by Day</b>")
        fig_line.update_traces(line_color="#0096EB", line_width=3)
        fig_line.update_layout(height=195, margin=CHART_MARGINS, paper_bgcolor=TRANS_BG, plot_bgcolor=TRANS_BG)
        st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

    # ROW 2
    r2_left, r2_right = st.columns([1.6, 2.4], gap="medium")

    with r2_left:
        city_sales = filtered_df.groupby(["city","lat","lon"])["revenue"].sum().reset_index()

        fig_map = px.scatter_mapbox(
            city_sales,
            lat="lat",
            lon="lon",
            size="revenue",
            color="revenue",
            zoom=3,
            height=515,
            title="<b>Total Sales by City</b>"
        )

        fig_map.update_layout(
            mapbox_style="carto-positron",
            margin=dict(l=10,r=10,t=40,b=30),
            paper_bgcolor=TRANS_BG
        )

        st.plotly_chart(fig_map, use_container_width=True)

    with r2_right:
        sub_t1, sub_t2 = st.columns(2)
        sub_b1, sub_b2 = st.columns(2)

        s_h = 220

        m_sales = filtered_df.groupby("model")["revenue"].sum().reset_index().sort_values("revenue", ascending=False).head(3)

        fig1 = px.bar(m_sales, x="model", y="revenue", title="<b>Total Sales by Model</b>", color_discrete_sequence=["#0096EB"])
        fig1.update_layout(height=s_h, margin=CHART_MARGINS, paper_bgcolor=TRANS_BG, plot_bgcolor=TRANS_BG)
        sub_t1.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

        pay_dist = filtered_df["payment_method"].value_counts().reset_index()
        fig2 = px.pie(pay_dist, names="payment_method", values="count", title="<b>Payment Methods</b>")
        fig2.update_layout(height=s_h, margin=CHART_MARGINS, paper_bgcolor=TRANS_BG)
        sub_t2.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        ratings = filtered_df["ratings"].value_counts().sort_index(ascending=False).reset_index()
        fig3 = px.funnel(ratings, y="ratings", x="count", title="<b>Customer Ratings</b>", color_discrete_sequence=["#0096EB"])
        fig3.update_layout(height=s_h, margin=CHART_MARGINS, paper_bgcolor=TRANS_BG, plot_bgcolor=TRANS_BG)
        sub_b1.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

        day_sales = filtered_df.groupby(filtered_df["order_date"].dt.day_name())["revenue"].sum().reset_index()
        fig4 = px.area(day_sales, x="order_date", y="revenue", title="<b>Sales by Day Name</b>")
        fig4.update_layout(height=s_h, margin=CHART_MARGINS, paper_bgcolor=TRANS_BG, plot_bgcolor=TRANS_BG)
        sub_b2.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})