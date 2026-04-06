import pandas as pd
import altair as alt
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Load & clean
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(BASE, "ds4200_final_data.csv"))
df["GDP"] = pd.to_numeric(
    df["Country GDP (millions USD)"].str.replace(r"[^\d.]", "", regex=True),
    errors="coerce"
)

df_no_world = df[df["Country"] != "World"]

# ---------------------------------------------------------------------------
# Region mapping
# ---------------------------------------------------------------------------
region_map = {
    # Americas
    "Antigua and Barbuda": "america", "Argentina": "america", "Bahamas": "america",
    "Barbados": "america", "Belize": "america", "Bermuda": "america",
    "Bolivia": "america", "Brazil": "america", "Canada": "america",
    "Chile": "america", "Colombia": "america", "Costa Rica": "america",
    "Cuba": "america", "Dominica": "america", "Dominican Republic": "america",
    "Ecuador": "america", "El Salvador": "america", "Greenland": "america",
    "Grenada": "america", "Guatemala": "america", "Guyana": "america",
    "Haiti": "america", "Honduras": "america", "Jamaica": "america",
    "Mexico": "america", "Nicaragua": "america", "Panama": "america",
    "Paraguay": "america", "Peru": "america", "Puerto Rico": "america",
    "Saint Kitts and Nevis": "america", "Saint Lucia": "america",
    "Saint Vincent and the Grenadines": "america", "Suriname": "america",
    "Trinidad and Tobago": "america", "United States": "america",
    "Uruguay": "america", "Venezuela": "america",
    # East Asia & Pacific
    "American Samoa": "east_asia_pacific", "Australia": "east_asia_pacific",
    "Brunei": "east_asia_pacific", "Cambodia": "east_asia_pacific",
    "China": "east_asia_pacific", "Cook Islands": "east_asia_pacific",
    "Fiji": "east_asia_pacific", "Guam": "east_asia_pacific",
    "Indonesia": "east_asia_pacific", "Japan": "east_asia_pacific",
    "Kiribati": "east_asia_pacific", "Laos": "east_asia_pacific",
    "Malaysia": "east_asia_pacific", "Marshall Islands": "east_asia_pacific",
    "Mongolia": "east_asia_pacific", "Myanmar": "east_asia_pacific",
    "Nauru": "east_asia_pacific", "New Zealand": "east_asia_pacific",
    "North Korea": "east_asia_pacific", "Northern Mariana Islands": "east_asia_pacific",
    "Palau": "east_asia_pacific", "Papua New Guinea": "east_asia_pacific",
    "Philippines": "east_asia_pacific", "Samoa": "east_asia_pacific",
    "Singapore": "east_asia_pacific", "Solomon Islands": "east_asia_pacific",
    "South Korea": "east_asia_pacific", "Taiwan": "east_asia_pacific",
    "Thailand": "east_asia_pacific", "Timor-Leste": "east_asia_pacific",
    "Tonga": "east_asia_pacific", "Tuvalu": "east_asia_pacific",
    "Vanuatu": "east_asia_pacific", "Vietnam": "east_asia_pacific",
    # Europe & Central Asia
    "Albania": "europe_central_asia", "Andorra": "europe_central_asia",
    "Armenia": "europe_central_asia", "Austria": "europe_central_asia",
    "Azerbaijan": "europe_central_asia", "Belarus": "europe_central_asia",
    "Belgium": "europe_central_asia", "Bosnia and Herzegovina": "europe_central_asia",
    "Bulgaria": "europe_central_asia", "Croatia": "europe_central_asia",
    "Cyprus": "europe_central_asia", "Denmark": "europe_central_asia",
    "Estonia": "europe_central_asia", "Finland": "europe_central_asia",
    "France": "europe_central_asia", "Georgia": "europe_central_asia",
    "Germany": "europe_central_asia", "Greece": "europe_central_asia",
    "Hungary": "europe_central_asia", "Iceland": "europe_central_asia",
    "Ireland": "europe_central_asia", "Italy": "europe_central_asia",
    "Kazakhstan": "europe_central_asia", "Kyrgyzstan": "europe_central_asia",
    "Latvia": "europe_central_asia", "Lithuania": "europe_central_asia",
    "Luxembourg": "europe_central_asia", "Malta": "europe_central_asia",
    "Moldova": "europe_central_asia", "Monaco": "europe_central_asia",
    "Montenegro": "europe_central_asia", "Netherlands": "europe_central_asia",
    "North Macedonia": "europe_central_asia", "Norway": "europe_central_asia",
    "Poland": "europe_central_asia", "Portugal": "europe_central_asia",
    "Romania": "europe_central_asia", "Russia": "europe_central_asia",
    "San Marino": "europe_central_asia", "Serbia": "europe_central_asia",
    "Slovakia": "europe_central_asia", "Slovenia": "europe_central_asia",
    "Spain": "europe_central_asia", "Sweden": "europe_central_asia",
    "Switzerland": "europe_central_asia", "Tajikistan": "europe_central_asia",
    "Turkey": "europe_central_asia", "Turkmenistan": "europe_central_asia",
    "Ukraine": "europe_central_asia", "United Kingdom": "europe_central_asia",
    "Uzbekistan": "europe_central_asia",
    # Middle East & North Africa
    "Algeria": "middle_east_north_africa", "Bahrain": "middle_east_north_africa",
    "Djibouti": "middle_east_north_africa", "Egypt": "middle_east_north_africa",
    "Iran": "middle_east_north_africa", "Iraq": "middle_east_north_africa",
    "Israel": "middle_east_north_africa", "Jordan": "middle_east_north_africa",
    "Kuwait": "middle_east_north_africa", "Lebanon": "middle_east_north_africa",
    "Libya": "middle_east_north_africa", "Mauritania": "middle_east_north_africa",
    "Morocco": "middle_east_north_africa", "Oman": "middle_east_north_africa",
    "Palestine": "middle_east_north_africa", "Qatar": "middle_east_north_africa",
    "Saudi Arabia": "middle_east_north_africa", "Syria": "middle_east_north_africa",
    "Tunisia": "middle_east_north_africa", "United Arab Emirates": "middle_east_north_africa",
    "Yemen": "middle_east_north_africa",
    # South Asia
    "Afghanistan": "south_asia", "Bangladesh": "south_asia",
    "Bhutan": "south_asia", "India": "south_asia",
    "Maldives": "south_asia", "Nepal": "south_asia",
    "Pakistan": "south_asia", "Sri Lanka": "south_asia",
    # Sub-Saharan Africa
    "Angola": "sub_saharan_africa", "Benin": "sub_saharan_africa",
    "Botswana": "sub_saharan_africa", "Burkina Faso": "sub_saharan_africa",
    "Burundi": "sub_saharan_africa", "Cameroon": "sub_saharan_africa",
    "Cape Verde": "sub_saharan_africa", "Central African Republic": "sub_saharan_africa",
    "Chad": "sub_saharan_africa", "Comoros": "sub_saharan_africa",
    "Congo": "sub_saharan_africa", "Equatorial Guinea": "sub_saharan_africa",
    "Eritrea": "sub_saharan_africa", "Eswatini": "sub_saharan_africa",
    "Ethiopia": "sub_saharan_africa", "Gabon": "sub_saharan_africa",
    "Gambia": "sub_saharan_africa", "Ghana": "sub_saharan_africa",
    "Guinea": "sub_saharan_africa", "Guinea-Bissau": "sub_saharan_africa",
    "Kenya": "sub_saharan_africa", "Lesotho": "sub_saharan_africa",
    "Liberia": "sub_saharan_africa", "Madagascar": "sub_saharan_africa",
    "Malawi": "sub_saharan_africa", "Mali": "sub_saharan_africa",
    "Mauritius": "sub_saharan_africa", "Mozambique": "sub_saharan_africa",
    "Namibia": "sub_saharan_africa", "Niger": "sub_saharan_africa",
    "Nigeria": "sub_saharan_africa", "Rwanda": "sub_saharan_africa",
    "Senegal": "sub_saharan_africa", "Seychelles": "sub_saharan_africa",
    "Sierra Leone": "sub_saharan_africa", "Somalia": "sub_saharan_africa",
    "South Africa": "sub_saharan_africa", "South Sudan": "sub_saharan_africa",
    "Sudan": "sub_saharan_africa", "Tanzania": "sub_saharan_africa",
    "Togo": "sub_saharan_africa", "Uganda": "sub_saharan_africa",
    "Zambia": "sub_saharan_africa", "Zimbabwe": "sub_saharan_africa",
}

disorder_cols = [
    "Depressive Disorders", "Anxiety Disorders",
    "Bipolar Disorders", "Schizophrenia", "Eating Disorders",
]

REGION_COLORS = {
    "america":                 "#e63946",
    "east_asia_pacific":       "#2196f3",
    "europe_central_asia":     "#4caf50",
    "middle_east_north_africa":"#ff9800",
    "south_asia":              "#9c27b0",
    "sub_saharan_africa":      "#795548",
    "other":                   "#90a4ae",
}

# ---------------------------------------------------------------------------
# Aggregate data (one row per country = mean across all years)
# ---------------------------------------------------------------------------
agg = (
    df_no_world
    .groupby("Country")[disorder_cols + ["GDP"]]
    .mean()
    .reset_index()
)
agg["region"] = agg["Country"].map(region_map).fillna("other")
agg = agg.dropna(subset=["GDP"])

# ---------------------------------------------------------------------------
# Altair chart
# ---------------------------------------------------------------------------
region_select = alt.param(
    name="Region",
    bind=alt.binding_radio(
        options=["all", "america", "east_asia_pacific", "europe_central_asia",
                 "middle_east_north_africa", "south_asia", "sub_saharan_africa"],
        name="Filter by Region: "
    ),
    value="all"
)

disorder_select = alt.param(
    name="Disorder",
    bind=alt.binding_select(
        options=disorder_cols,
        name="Disorder Type: "
    ),
    value="Depressive Disorders"
)

color_domain = list(REGION_COLORS.keys())
color_range  = list(REGION_COLORS.values())

chart = (
    alt.Chart(agg)
    .mark_circle(size=110, stroke="white", strokeWidth=0.8)
    .transform_fold(disorder_cols, as_=["disorder_type", "prevalence"])
    .transform_filter("datum.disorder_type == Disorder")
    .encode(
        x=alt.X(
            "GDP:Q",
            scale=alt.Scale(type="log"),
            title="Country GDP — millions USD (log scale)",
            axis=alt.Axis(grid=True, gridColor="#e9ecef", tickCount=6),
        ),
        y=alt.Y(
            "prevalence:Q",
            title="Mean Prevalence (% of population)",
            axis=alt.Axis(grid=True, gridColor="#e9ecef"),
        ),
        color=alt.condition(
            "Region == 'all' || datum.region == Region",
            alt.Color(
                "region:N",
                scale=alt.Scale(domain=color_domain, range=color_range),
                legend=alt.Legend(
                    title="World Region",
                    orient="right",
                    labelFontSize=12,
                    titleFontSize=13,
                    symbolSize=120,
                ),
            ),
            alt.value("#dee2e6"),
        ),
        opacity=alt.condition(
            "Region == 'all' || datum.region == Region",
            alt.value(0.88), alt.value(0.08),
        ),
        size=alt.condition(
            "Region == 'all' || datum.region == Region",
            alt.value(120), alt.value(60),
        ),
        tooltip=[
            alt.Tooltip("Country:N",    title="Country"),
            alt.Tooltip("region:N",     title="Region"),
            alt.Tooltip("prevalence:Q", title="Avg Prevalence (%)", format=".3f"),
            alt.Tooltip("GDP:Q",        title="GDP (M USD)",        format=",.0f"),
        ],
    )
    .add_params(region_select, disorder_select)
    .properties(width="container", height=520)
    .configure_axis(labelFontSize=12, titleFontSize=13,
                    labelColor="#495057", titleColor="#343a40")
    .configure_legend(labelFontSize=12, titleFontSize=13)
    .configure_view(strokeWidth=0, fill="transparent")
)

chart_spec = json.dumps(chart.to_dict())
