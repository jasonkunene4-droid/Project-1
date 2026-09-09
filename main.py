import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Nassau Candy - Route Efficiency Dashboard")

# Factory Coordinates from brief
factory_coords = {
    "Lot's O' Nuts": [32.881893, -111.768036],
    "Wicked Choccy's": [32.076176, -81.088371],
    "Sugar Shack": [48.11914, -96.18115],
    "Secret Factory": [41.446333, -90.565487],
    "The Other Factory": [35.1175, -89.971107]
}

file = st.file_uploader("Upload your clean CSV file here", type="csv")

if file:
    df = pd.read_csv(file)
    if 'Lead_Time_Days' not in df.columns:
        df['Lead_Time_Days'] = (pd.to_datetime(df['Ship Date']) - pd.to_datetime(df['Order Date'])).dt.days
    if 'Route' not in df.columns and 'Factory' in df.columns:
        df['Route'] = df['Factory'].astype(str) + " -> " + df['State/Province'].astype(str)

    st.success(f"Loaded {len(df)} rows!")

    # --- OUTLIER FIX ---
    st.write(f"Original Avg: {df['Lead_Time_Days'].mean():.1f} days")
    df_clean = df[(df['Lead_Time_Days'] >= 10) & (df['Lead_Time_Days'] <= 180)].copy()
    df_clean['Is_Delayed'] = df_clean['Lead_Time_Days'] > 120
    st.write(f"After 10-180 day filter: {len(df_clean)} rows, Avg {df_clean['Lead_Time_Days'].mean():.1f} days | Removed {len(df)-len(df_clean)} outliers")

    # --- FILTERS (Required) ---
    st.sidebar.header("Filters")
    region_sel = st.sidebar.multiselect("Region", df_clean['Region'].unique())
    state_sel = st.sidebar.multiselect("State/Province", df_clean['State/Province'].unique() if 'State/Province' in df_clean.columns else [])
    shipmode_sel = st.sidebar.multiselect("Ship Mode", df_clean['Ship Mode'].unique())
    threshold = st.sidebar.slider("Lead-time threshold", 10, 180, 120)

    filtered = df_clean.copy()
    if region_sel:
        filtered = filtered[filtered['Region'].isin(region_sel)]
    if state_sel and 'State/Province' in filtered.columns:
        filtered = filtered[filtered['State/Province'].isin(state_sel)]
    if shipmode_sel:
        filtered = filtered[filtered['Ship Mode'].isin(shipmode_sel)]
    filtered = filtered[filtered['Lead_Time_Days'] <= threshold]

    # --- KPIs ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Lead Time", f"{filtered['Lead_Time_Days'].mean():.1f} days")
    c2.metric("Total Shipments", f"{len(filtered)}")
    c3.metric("Factories", f"{filtered['Factory'].nunique() if 'Factory' in filtered.columns else 5}")
    c4.metric("Delay %", f"{filtered['Is_Delayed'].mean()*100:.1f}%")

    # --- Ship Mode Comparison ---
    st.subheader("Ship Mode Performance")
    if 'Ship Mode' in filtered.columns:
        st.bar_chart(filtered.groupby('Ship Mode')['Lead_Time_Days'].mean())

    # --- Geographic Map ---
    st.subheader("Factory Locations (Geographic Bottleneck)")
    map_df = pd.DataFrame([{"Factory": k, "lat": v[0], "lon": v[1]} for k, v in factory_coords.items()])
    st.map(map_df)

    # --- Route Drill-Down ---
    route_stats = filtered.groupby('Route')['Lead_Time_Days'].agg(['mean','count']).reset_index().rename(columns={'mean':'Avg_Days','count':'Volume'})
    st.subheader("Top 10 Fastest Routes")
    st.dataframe(route_stats.nsmallest(10, 'Avg_Days'))
    st.subheader("Bottom 10 Slowest Routes")
    st.dataframe(route_stats.nlargest(10, 'Avg_Days'))