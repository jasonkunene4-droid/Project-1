import pandas as pd
import numpy as np

df = pd.read_csv("/content/Nassau Candy Distributor (1).csv")
df.columns = df.columns.str.strip()

# Factory map (keep yours)
factory_map = {
    'Wonka Bar - Nutty Crunch Surprise': "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows': "Lot's O' Nuts",
    'Wonka Bar -Scrumdiddlyumptious': "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate': "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel': "Wicked Choccy's",
    'Laffy Taffy': 'Sugar Shack', 'SweeTARTS': 'Sugar Shack',
    'Nerds': 'Sugar Shack', 'Fun Dip': 'Sugar Shack',
    'Fizzy Lifting Drinks': 'Sugar Shack',
    'Everlasting Gobstopper': 'Secret Factory',
    'Lickable Wallpaper': 'Secret Factory',
    'Wonka Gum': 'Secret Factory', 'Kazookles': 'Secret Factory',
    'Hair Toffee': 'The Other Factory'
}
df['Factory'] = df['Product Name'].map(factory_map)

# --- CORRECT LEAD TIME LOGIC ---
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')

# Raw diff, no year forcing
df['Lead_Time_Days'] = (df['Ship Date'] - df['Order Date']).dt.days

print("Before cleaning:")
print(df['Lead_Time_Days'].describe())

# What is dirty?
print(f"\nNegative lead times: {(df['Lead_Time_Days'] < 0).sum()}")
print(f"Over 60 days: {(df['Lead_Time_Days'] > 60).sum()}")
print(df[df['Lead_Time_Days'] > 60][['Order Date','Ship Date','Lead_Time_Days']].head())

# REALISTIC CLEAN: Keep 0-30 days for candy distribution
# 60 max if you want to be generous, NOT 365
df_clean = df[(df['Lead_Time_Days'] >= 0) & (df['Lead_Time_Days'] <= 30)].copy()

print(f"\nOriginal: {len(df)} -> Clean: {len(df_clean)}")
print(f"FIXED Avg Lead Time: {df_clean['Lead_Time_Days'].mean():.1f} days") # Should be ~6-10 days now

# --- ADD WHAT EVALUATOR ASKED ---
df_clean['profit_margin'] = df_clean['Gross Profit'] / df_clean['Sales'] * 100
df_clean['Month'] = df_clean['Order Date'].dt.to_period('M').astype(str)

# Factory summary that actually makes sense
factory_summary = df_clean.groupby('Factory').agg(
    Avg_Lead_Time=('Lead_Time_Days', 'mean'),
    Avg_Cost=('Cost', 'mean'),
    Total_Orders=('Order ID', 'count'),
    Total_Profit=('Gross Profit', 'sum'),
    Avg_Margin=('profit_margin', 'mean')
).round(2).sort_values('Avg_Lead_Time', ascending=False)

print(factory_summary)

# Save
df_clean.to_csv('Nassau_Candy_Clean_FIXED.csv', index=False)
