import streamlit as st
import pandas as pd
import plotly.express as px


number = st.slider("Pick a number: ", min_value=1, max_value=10)
st.text("Your number is " + str(number))

# Load Data
file_path = "C:/Users/max_x/ucb/A - macss/2025 Spring/Climate TRACE & CLEE/Data/test-4-smac/smac.csv"
df = pd.read_csv(file_path)

# Basic Preprocessing
df['year'] = pd.to_datetime(df['start_time']).dt.year
latest_year = df['year'].max()

# Filtered datasets
df_gas_type = df[df['gas'].isin(['co2', 'ch4', 'n2o'])]
df_ch4 = df[df['gas'] == 'ch4']
df_gas_total = df_ch4 

# Define sector mapping (updated and expanded)
sector_map = {
    # Energy and Power
    "electricity-generation": "power",
    "solid-fuel-transformation": "power",
    "heat-plants": "power",

    # Manufacturing
    "cement": "manufacturing",
    "chemicals": "manufacturing",
    "aluminum": "manufacturing",
    "iron-and-steel": "manufacturing",
    "glass": "manufacturing",
    "lime": "manufacturing",
    "food-beverage-tobacco": "manufacturing",
    "wood-and-wood-products": "manufacturing",
    "pulp-and-paper": "manufacturing",
    "textiles-leather-apparel": "manufacturing",
    "other-manufacturing": "manufacturing",
    "petrochemical-steam-cracking": "manufacturing",
    "other-chemicals": "manufacturing",
    "other-metals": "manufacturing",

    # Transportation
    "road-transportation": "transportation",
    "domestic-aviation": "transportation",
    "international-aviation": "transportation",
    "railways": "transportation",
    "other-transport": "transportation",
    "domestic-shipping": "transportation",
    "international-shipping": "transportation",

    # Agriculture
    "crop-residues": "agriculture",
    "cropland-fires": "agriculture",
    "rice-cultivation": "agriculture",
    "synthetic-fertilizer-application": "agriculture",
    "other-agricultural-soil-emissions": "agriculture",
    "enteric-fermentation-cattle-pasture": "agriculture",
    "enteric-fermentation-cattle-operation": "agriculture",
    "enteric-fermentation-other": "agriculture",
    "manure-left-on-pasture-cattle": "agriculture",
    "manure-management-cattle-operation": "agriculture",
    "manure-management-other": "agriculture",
    "manure-applied-to-soils": "agriculture",

    # Fossil Fuels
    "coal-mining": "fossil-fuel-operations",
    "oil-and-gas-production": "fossil-fuel-operations",
    "oil-and-gas-transport": "fossil-fuel-operations",
    "oil-and-gas-refining": "fossil-fuel-operations",
    "other-fossil-fuel-operations": "fossil-fuel-operations",

    # Waste
    "solid-waste-disposal": "waste",
    "biological-treatment-of-solid-waste-and-biogenic": "waste",
    "incineration-and-open-burning-of-waste": "waste",
    "domestic-wastewater-treatment-and-discharge": "waste",
    "industrial-wastewater-treatment-and-discharge": "waste",

    # Land Use
    "forest-land-clearing": "land-use-change",
    "forest-land-degradation": "land-use-change",
    "forest-land-fires": "land-use-change",
    "net-forest-land": "land-use-change",
    "net-shrubgrass": "land-use-change",
    "net-wetland": "land-use-change",
    "wetland-fires": "land-use-change",
    "shrubgrass-fires": "land-use-change",
    "removals": "land-use-change",
    "water-reservoirs": "land-use-change",

    # Minerals
    "bauxite-mining": "mineral-extraction",
    "copper-mining": "mineral-extraction",
    "iron-mining": "mineral-extraction",
    "sand-quarrying": "mineral-extraction",
    "rock-quarrying": "mineral-extraction",
    "other-mining-quarrying": "mineral-extraction",

    # Other
    "fluorinated-gases": "fluorinated-gases",
    "residential-onsite-fuel-usage": "other-energy-use",
    "non-residential-onsite-fuel-usage": "other-energy-use",
    "other-onsite-fuel-usage": "other-energy-use",
    "other-energy-use": "other-energy-use"
}

# App Settings
st.set_page_config(layout="wide")
st.title("SMAC Members Methane Inventory")
st.markdown("This is a testing version, if you see some warning below the table, just change a differnet location B in the Comparison Tool")

# Tabs
tab2, tab1, tab3 = st.tabs(["SMAC Group Methane Emissions", " Subnational Methane Emissions","Comparison Tool"])

# -------- TAB 1: Country/Sector Breakdown --------
with tab1:
    st.subheader("1️⃣Country & Subnational Emissions Breakdown")

    countries = sorted(df['iso3_country'].unique())
    selected_country = st.selectbox("Select Country", countries)

    locations = sorted(df[df['iso3_country'] == selected_country]['location'].unique())
    selected_location = st.selectbox("Select Location (State/City)", locations)

    available_years = sorted(df['year'].unique())

    # PIE CHART - select year
    year_pie = st.selectbox("Select Year for Gas Breakdown", available_years, index=available_years.index(latest_year))
    loc_gas_df = df_gas_type[
        (df_gas_type['iso3_country'] == selected_country) &
        (df_gas_type['location'] == selected_location) &
        (df_gas_type['year'] == year_pie)
    ]
    st.subheader(f"Gas Emissions Breakdown ({year_pie})")
    pie_sum = loc_gas_df.groupby('gas')[['asset_emissions', 'remainder_emissions']].sum().reset_index()
    pie_sum['total'] = pie_sum['asset_emissions'] + pie_sum['remainder_emissions']
    fig_pie = px.pie(pie_sum, names='gas', values='total', title=f"{selected_location} – {year_pie} Gas Breakdown (Original Gases)")
    st.plotly_chart(fig_pie, use_container_width=True)

    # SECTOR OVER TIME - CH4
    st.subheader("2️⃣ Emissions by Sector Over Time (CH4)")
    loc_total_df = df_gas_total[(df_gas_total['iso3_country'] == selected_country) & (df_gas_total['location'] == selected_location)]
    bar_df = loc_total_df.groupby(['year', 'original_inventory_sector'])[['asset_emissions', 'remainder_emissions']].sum().reset_index()
    bar_df['total'] = bar_df['asset_emissions'] + bar_df['remainder_emissions']
    bar_df = bar_df[bar_df['total'] > 0]
    bar_df['sector'] = bar_df['original_inventory_sector'].map(sector_map).fillna('other')
    grouped = bar_df.groupby(['year', 'sector'])['total'].sum().reset_index()
    fig_bar = px.bar(grouped, x='year', y='total', color='sector',
                     labels={'total': 'Emissions (CH4)'}, title="Sectoral Emissions Over Time")
    st.plotly_chart(fig_bar, use_container_width=True)

    # SUBSECTOR BREAKDOWN - select year
    year_sub = st.selectbox("Select Year for Subsector Breakdown", available_years, index=available_years.index(latest_year))
    sub_df = loc_total_df[loc_total_df['year'] == year_sub].groupby('original_inventory_sector')[['asset_emissions', 'remainder_emissions']].sum().reset_index()
    sub_df['total'] = sub_df['asset_emissions'] + sub_df['remainder_emissions']
    sub_df = sub_df[sub_df['total'] > 0]  # Remove negative and zero values

    st.subheader(f"3️⃣ Subsector Emissions Breakdown ({year_sub}, CH4)")
    fig_sub_bar = px.bar(sub_df.sort_values(by='total', ascending=False), x='original_inventory_sector', y='total',
                     labels={'total': 'Emissions (CH4)'}, title=f"{selected_location} – Subsector Breakdown ({year_sub})")

    fig_sub_pie = px.pie(
        sub_df,
        names='original_inventory_sector',
        values='total',
        title=f"{selected_location} – Subsector Breakdown Pie Chart ({year_sub})"
    )
    fig_sub_pie.update_traces(
        textinfo='none',
        pull=[0.05]*len(sub_df),
        insidetextorientation='radial'
    )
    fig_sub_pie.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        legend=dict(font=dict(size=10)),
        showlegend=True
    )

    st.plotly_chart(fig_sub_bar, use_container_width=True)
    st.plotly_chart(fig_sub_pie, use_container_width=True)


# -------- TAB 2: City Emissions Overview --------
with tab2:
    st.header("Subnational Emissions Rankings")

    year_city = st.selectbox("Select Year for Top Emitting Locations (CH₄ only)", available_years, index=available_years.index(latest_year))
    city_df = (
        df_ch4[df_ch4['year'] == year_city]
        .groupby(['iso3_country', 'location'])[['asset_emissions', 'remainder_emissions']]
        .sum()
        .reset_index()
    )
    city_df['total'] = city_df['asset_emissions'] + city_df['remainder_emissions']
    top_cities = city_df.sort_values(by='total', ascending=False).head(20)

    fig_city = px.bar(top_cities, x='location', y='total', color='iso3_country',
                      title=f"Top 20 Emitting Locations by CH₄ – {year_city}", labels={'total': 'Emissions (CH₄)'})
    st.plotly_chart(fig_city, use_container_width=True)

    # Display the top 20 cities in a table
    st.subheader(f"Top 20 Emitting Locations - {year_city}")
    st.dataframe(top_cities[['iso3_country', 'location', 'total']].sort_values(by='total', ascending=False))

    # -------- TAB 3: Compare CH₄ Emissions --------
with tab3:
    st.header("Compare CH₄ Emissions")
    available_years = sorted(df['year'].unique())
    comparison_year = st.selectbox("Select Year", available_years, index=available_years.index(latest_year))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Location A")
        country_a = st.selectbox("Country A", sorted(df['iso3_country'].unique()), key='a')
        location_a = st.selectbox("State/City A", sorted(df[df['iso3_country'] == country_a]['location'].unique()), key='loc_a')

    with col2:
        st.subheader("Location B")
        country_b = st.selectbox("Country B", sorted(df['iso3_country'].unique()), key='b')
        location_b = st.selectbox("State/City B", sorted(df[df['iso3_country'] == country_b]['location'].unique()), key='loc_b')

    # Get data for both locations
    def get_comparison_df(country, location):
        temp_df = df_ch4[(df_ch4['iso3_country'] == country) & (df_ch4['location'] == location)]
        temp_df = temp_df.groupby(['year', 'original_inventory_sector'])[['asset_emissions', 'remainder_emissions']].sum().reset_index()
        temp_df['total'] = temp_df['asset_emissions'] + temp_df['remainder_emissions']
        temp_df = temp_df[temp_df['total'] > 0]
        temp_df['sector'] = temp_df['original_inventory_sector'].map(sector_map).fillna('other')
        return temp_df

    df_a = get_comparison_df(country_a, location_a)
    df_b = get_comparison_df(country_b, location_b)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f"{location_a} ({comparison_year}) - Emissions by Sector Over Time")
        fig_time_a = px.bar(df_a, x='year', y='total', color='sector',
                            labels={'total': 'CH₄ Emissions'}, title=f"{location_a} – CH₄ Emissions by Sector Over Time")
        st.plotly_chart(fig_time_a, use_container_width=True)

        # Additional visualizations for location A as needed...
        st.subheader(f"{location_a} ({comparison_year}) - Bar Chart")
        fig_a = px.bar(df_a.sort_values(by='total', ascending=False), x='sector', y='total',
                       labels={'total': 'CH₄ Emissions'}, title=f"{location_a} – CH₄ Emissions by Subsector")
        st.plotly_chart(fig_a, use_container_width=True, key='fig_a')

        st.subheader(f"{location_a} ({comparison_year}) - Pie Chart")
        fig_pie_a = px.pie(df_a, names='sector', values='total', title=f"{location_a} – CH₄ Emissions by Subsector")
        st.plotly_chart(fig_pie_a, use_container_width=True)

        st.subheader("Data Table - Location A")
        st.dataframe(df_a)


    with col4:
        st.subheader(f"{location_b} ({comparison_year}) - Emissions by Sector Over Time")
        fig_time_b = px.bar(df_b, x='year', y='total', color='sector',
                            labels={'total': 'CH₄ Emissions'}, title=f"{location_b} – CH₄ Emissions by Sector Over Time")
        st.plotly_chart(fig_time_b, use_container_width=True)

        # Additional visualizations for location B as needed...
        st.subheader(f"{location_b} ({comparison_year}) - Bar Chart")
        fig_b = px.bar(df_b.sort_values(by='total', ascending=False), x='sector', y='total',
                       labels={'total': 'CH₄ Emissions'}, title=f"{location_b} – CH₄ Emissions by Subsector")
        st.plotly_chart(fig_b, use_container_width=True, key='fig_b')

        st.subheader(f"{location_b} ({comparison_year}) - Pie Chart")
        fig_pie_b = px.pie(df_b, names='sector', values='total', title=f"{location_b} – CH₄ Emissions by Subsector")
        st.plotly_chart(fig_pie_b, use_container_width=True)

        st.subheader("Data Table - Location B")
        st.dataframe(df_b)

