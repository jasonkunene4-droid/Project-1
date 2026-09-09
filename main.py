import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Dashboard", layout="wide")
st.title("🍫 Nassau Candy - Route & Profit Efficiency Dashboard")
st.caption("Dataset: 4130 cleaned records | Auto-loaded from GitHub")

# Load data automatically
@st.cache_data
def load_data():
    return pd.read_csv("Nassau_Candy_Clean_4130.csv")

df = load_data()

# Convert dates
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Sidebar filters
st.sidebar.header("Filters")
division = st.sidebar.multiselect("Division", df['Division'].unique(), default=df['Division'].unique())
region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())

filtered = df[(df['Division'].isin(division)) & (df['Region'].isin(region))]

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", len(filtered))
c2.metric("Total Sales", f"${filtered['Sales'].sum():,.2f}")
c3.metric("Total Profit", f"${filtered['Gross Profit'].sum():,.2f}")
c4.metric("Avg Lead Time", f"{filtered['Lead_Time_Days'].mean():.1f} days")

st.divider()

# Charts
col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(filtered.groupby('Division')['Sales'].sum().reset_index(), 
                  x='Division', y='Sales', title="Sales by Division", color='Division')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(filtered.groupby('Factory')['Gross Profit'].sum().reset_index().sort_values('Gross Profit', ascending=False),
                  x='Factory', y='Gross Profit', title="Profit by Factory")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    fig3 = px.scatter(filtered, x='Lead_Time_Days', y='Gross Profit', color='Ship Mode',
                      title="Lead Time vs Profit", hover_data=['Product Name'])
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.pie(filtered, names='Region', values='Sales', title="Sales by Region")
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("Data Preview")
st.dataframe(filtered.head(100), use_container_width=True)
