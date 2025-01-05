import streamlit as st
import pandas as pd
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='WQD7004 Alternative Assessment 1',
    page_icon=':airplane:',  # This is an emoji shortcode. Could be a URL too.
)

# -------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_data():
    """Load and preprocess data from CSV files."""
    # Load data
    arrivals_file = Path(__file__).parent / 'data/foreign_arrivals.csv'
    poe_file = Path(__file__).parent / 'data/poe.csv'

    foreign_arrival_df = pd.read_csv(arrivals_file)
    poe_df = pd.read_csv(poe_file)

    # Preprocess data
    foreign_arrival_df['date'] = pd.to_datetime(foreign_arrival_df['date'])
    foreign_arrival_df['year'] = foreign_arrival_df['date'].dt.year

    # Merge dataframes
    merged_df = foreign_arrival_df.merge(poe_df, on='poe', how='left')

    return merged_df

# Load data
data_df = get_data()

# Debugging: View dataset columns and sample
# st.write("Merged DataFrame Sample:", data_df.head())
# st.write("Merged DataFrame Columns:", data_df.columns)

# -------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :airplane: Foreign Arrivals Dashboard

Explore data on foreign arrivals by point of entry (POE) and country.
'''

# Year range slider (set default to the entire available range)
min_year = data_df['year'].min()
max_year = data_df['year'].max()

from_year, to_year = st.slider(
    'Select the year range:',
    min_value=min_year,
    max_value=max_year,
    value=[min_year, max_year]  # Default to full range
)

# Country and POE selection with "Select All" option
countries = data_df['country'].unique().tolist()
poes = data_df['poe'].unique().tolist()

# Add "Select All" option to countries and POEs
countries.insert(0, 'Select All')
poes.insert(0, 'Select All')

# Country filter
selected_countries = st.multiselect(
    'Select countries:',
    countries,
    default=countries[1:]  # By default, all countries are selected (except "Select All")
)

# POE filter
selected_poes = st.multiselect(
    'Select points of entry (POE):',
    poes,
    default=poes[1:]  # By default, all POEs are selected (except "Select All")
)

# Handle "Select All" logic
if 'Select All' in selected_countries:
    selected_countries = countries[1:]  # Exclude "Select All" option
if 'Select All' in selected_poes:
    selected_poes = poes[1:]  # Exclude "Select All" option

# Filter the data based on selections
filtered_data_df = data_df[
    (data_df['country'].isin(selected_countries)) &
    (data_df['poe'].isin(selected_poes)) &
    (data_df['year'] >= from_year) &
    (data_df['year'] <= to_year)
]

# Display key metrics: Total Arrivals
st.header(f'Total Arrivals in {to_year}', divider='gray')

# Filter data for the selected year and selected countries/POEs
filtered_data_for_year = filtered_data_df[filtered_data_df['year'] == to_year]

# Group the filtered data by country and sum the arrivals
summary = filtered_data_for_year.groupby('country')['arrivals'].sum()

# Check if there is no data available for the selected year
if summary.empty:
    st.write("No data available for the selected year and filters.")
else:
    # Display the summary as individual metrics
    cols = st.columns(min(len(summary), 4))  # Limit number of columns to 4 for readability

    for i, (country, total) in enumerate(summary.items()):
        with cols[i % len(cols)]:  # Distribute metrics across available columns
            st.metric(
                label=f'{country} Total Arrivals',
                value=f'{total:,}'  # Format number with commas
            )


# Plotting arrival trends
st.header('Arrivals Over Time', divider='gray')

st.line_chart(
    filtered_data_df.groupby(['year', 'country'])['arrivals'].sum().unstack(),
    use_container_width=True
)

# Map visualization
st.header('Points of Entry Map', divider='gray')

# Rename 'long' to 'lon' for compatibility with st.map
data_for_map = filtered_data_df[['lat', 'long']].dropna().drop_duplicates()
data_for_map = data_for_map.rename(columns={'long': 'lon'})

# Display the map
st.map(data_for_map, zoom=5)

# Additional visualizations

# 1. Total Arrivals by POE and Country (Bar Chart)
st.header('Total Arrivals by POE and Country', divider='gray')

# Group data for visualization (filtered by selected countries and POEs)
total_arrivals_by_poe = filtered_data_df.groupby(['poe', 'country'])['arrivals'].sum().unstack()

# Plot bar chart
st.bar_chart(total_arrivals_by_poe, use_container_width=True)

# 2. Monthly Arrival Distribution (Line Chart)
st.header('Monthly Arrival Distribution', divider='gray')

# Filter data to include selected year and countries
filtered_data_df['month'] = filtered_data_df['date'].dt.month
monthly_arrivals = filtered_data_df.groupby(['month', 'country'])['arrivals'].sum().unstack()

# Plot monthly distribution
st.line_chart(monthly_arrivals, use_container_width=True)
