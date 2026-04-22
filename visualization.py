import pandas as pd
import numpy as np
import altair as alt
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Load & clean
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(BASE, "ds4200_final_data_clean.csv"))
df["GDP"] = pd.to_numeric(df["Country GDP (millions USD)"], errors="coerce")

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

REGION_LABELS = {
    "america":                  "Americas",
    "east_asia_pacific":        "East Asia & Pacific",
    "europe_central_asia":      "Europe & Central Asia",
    "middle_east_north_africa": "Middle East & North Africa",
    "south_asia":               "South Asia",
    "sub_saharan_africa":       "Sub-Saharan Africa",
    "other":                    "Other",
}
agg["region_label"] = agg["region"].map(REGION_LABELS)

# ---------------------------------------------------------------------------
# Altair chart
# ---------------------------------------------------------------------------
region_select = alt.param(
    name="Region",
    bind=alt.binding_radio(
        options=["all", "america", "east_asia_pacific", "europe_central_asia",
                 "middle_east_north_africa", "south_asia", "sub_saharan_africa"],
        labels=["All", "Americas", "East Asia & Pacific", "Europe & Central Asia",
                "Middle East & N. Africa", "South Asia", "Sub-Saharan Africa"],
        name="Region: "
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
color_range = list(REGION_COLORS.values())

# ---------------------------------------------------------------------------
# Shared legend style — applied consistently across all charts
# ---------------------------------------------------------------------------
_LEGEND_STYLE = dict(
    titleFontSize=12,
    titleFontWeight="bold",
    titleColor="#343a40",
    titlePadding=8,
    labelFontSize=11,
    labelColor="#495057",
    labelPadding=6,
    padding=10,
    fillColor="#ffffff",
    strokeColor="#dde3f0",
    cornerRadius=6,
)

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
                    labelExpr=(
                        "{'america': 'Americas'"
                        ", 'east_asia_pacific': 'East Asia & Pacific'"
                        ", 'europe_central_asia': 'Europe & Central Asia'"
                        ", 'middle_east_north_africa': 'Middle East & North Africa'"
                        ", 'south_asia': 'South Asia'"
                        ", 'sub_saharan_africa': 'Sub-Saharan Africa'"
                        ", 'other': 'Other'}[datum.value]"
                    ),
                    symbolSize=100,
                    symbolType="circle",
                    symbolStrokeWidth=0,
                    rowPadding=5,
                    **_LEGEND_STYLE,
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
            alt.Tooltip("Country:N",      title="Country"),
            alt.Tooltip("region_label:N", title="Region"),
            alt.Tooltip("prevalence:Q",   title="Avg Prevalence (%)", format=".3f"),
            alt.Tooltip("GDP:Q",          title="GDP (M USD)",        format=",.0f"),
        ],
    )
    .add_params(region_select, disorder_select)
    .properties(width="container", height=520)
    .configure_axis(labelFontSize=12, titleFontSize=13,
                    labelColor="#495057", titleColor="#343a40")
    .configure_legend(labelFontSize=11, titleFontSize=12)
    .configure_view(strokeWidth=0, fill="transparent")
)

chart_spec = json.dumps(chart.to_dict())

# ---------------------------------------------------------------------------
# Chart 2: Top 10 Countries by Max Anxiety Disorders (replicates chart.js)
# ---------------------------------------------------------------------------
top10_anxiety = (
    df_no_world.groupby("Country")["Anxiety Disorders"]
    .max()
    .reset_index()
    .nlargest(10, "Anxiety Disorders")
    .sort_values("Anxiety Disorders", ascending=True)  # ascending so highest is at top in horizontal bar
)

anxiety_chart = (
    alt.Chart(top10_anxiety)
    .mark_bar(color="#2171b5", cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
    .encode(
        x=alt.X(
            "Anxiety Disorders:Q",
            title="Max Anxiety Disorders (% of population)",
            axis=alt.Axis(grid=True, gridColor="#e9ecef",
                          labelFontSize=12, titleFontSize=13,
                          labelColor="#495057", titleColor="#343a40"),
        ),
        y=alt.Y("Country:N", sort=None, title=None,
                axis=alt.Axis(labelFontSize=12, labelColor="#495057")),
        tooltip=[
            alt.Tooltip("Country:N", title="Country"),
            alt.Tooltip("Anxiety Disorders:Q", format=".3f", title="Max Prevalence (%)"),
        ],
    )
    .properties(width="container", height=380)
)

_anxiety_dict = anxiety_chart.to_dict()
# Inline named datasets so the spec is self-contained
if "datasets" in _anxiety_dict and "data" in _anxiety_dict:
    _name = _anxiety_dict["data"].get("name")
    if _name and _name in _anxiety_dict["datasets"]:
        _anxiety_dict["data"] = {"values": _anxiety_dict["datasets"][_name]}
        del _anxiety_dict["datasets"]
anxiety_top10_spec = json.dumps(_anxiety_dict)

# ---------------------------------------------------------------------------
# Chart 3: Grouped Bar — Top & Bottom 10 GDP Countries, all disorders (2019)
# ---------------------------------------------------------------------------
data_2019 = df_no_world[df_no_world["Year"] == 2019].copy()
data_2019 = data_2019.dropna(subset=["GDP"])

top10_gdp    = data_2019.nlargest(10,  "GDP")[["Country"] + disorder_cols].copy()
bottom10_gdp = data_2019.nsmallest(10, "GDP")[["Country"] + disorder_cols].copy()

top10_gdp["GDP Group"]    = "Top 10 Highest GDP Countries"
bottom10_gdp["GDP Group"] = "Bottom 10 Lowest GDP Countries"

gdp_long = (
    pd.concat([top10_gdp, bottom10_gdp])
    .melt(id_vars=["Country", "GDP Group"], value_vars=disorder_cols,
          var_name="Disorder", value_name="Prevalence")
)

DISORDER_COLOR_RANGE = ["#5c6bc0", "#26a69a", "#ef5350", "#8d6e63", "#ec407a"]

_disorder_scale = alt.Scale(domain=disorder_cols, range=DISORDER_COLOR_RANGE)

def _make_bar_panel(data, panel_title):
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X("Country:N", title=None,
                    axis=alt.Axis(labelAngle=-35, labelFontSize=11,
                                  labelColor="#495057")),
            xOffset=alt.XOffset("Disorder:N"),
            y=alt.Y("Prevalence:Q", title="Percent (%) of Population",
                    axis=alt.Axis(grid=True, gridColor="#e9ecef",
                                  labelFontSize=11, titleFontSize=12,
                                  labelColor="#495057", titleColor="#343a40")),
            color=alt.Color("Disorder:N", scale=_disorder_scale, legend=None),
            tooltip=[
                alt.Tooltip("Country:N",    title="Country"),
                alt.Tooltip("Disorder:N",   title="Disorder"),
                alt.Tooltip("Prevalence:Q", format=".3f", title="Prevalence (%)"),
            ],
        )
        .properties(width="container", height=260,
                    title=alt.Title(panel_title, fontSize=13, fontWeight="bold",
                                   color="#0d1b4b", anchor="start", offset=8))
        .configure_view(strokeWidth=1, stroke="#dde3f0")
    )
    # Inline the data so named-dataset lookup doesn't fail
    d = chart.to_dict()
    if "datasets" in d and "data" in d:
        name = d["data"].get("name")
        if name and name in d["datasets"]:
            d["data"] = {"values": d["datasets"][name]}
            del d["datasets"]
    return json.dumps(d)

top_long    = gdp_long[gdp_long["GDP Group"] == "Top 10 Highest GDP Countries"]
bottom_long = gdp_long[gdp_long["GDP Group"] == "Bottom 10 Lowest GDP Countries"]

gdp_top_spec    = _make_bar_panel(top_long,    "Top 10 Highest GDP Countries")
gdp_bottom_spec = _make_bar_panel(bottom_long, "Bottom 10 Lowest GDP Countries")

# Keep gdp_grouped_bar_spec as a tuple for backwards-compat import
gdp_grouped_bar_spec = (gdp_top_spec, gdp_bottom_spec)

# ---------------------------------------------------------------------------
# Globe land GeoJSON — fetched once at build time so pages work from file://
# ---------------------------------------------------------------------------
def _fetch_land_geojson():
    """Download world-atlas TopoJSON and decode land feature → compact GeoJSON."""
    import urllib.request
    try:
        url = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
        with urllib.request.urlopen(url, timeout=15) as _r:
            topo = json.loads(_r.read())
    except Exception:
        return "null"
    tf = topo.get("transform", {})
    kx, ky = tf.get("scale", [1, 1])
    tx, ty = tf.get("translate", [0, 0])
    raw_arcs = topo["arcs"]
    def _arc(idx):
        pts, x, y = [], 0, 0
        for dx, dy in raw_arcs[idx if idx >= 0 else ~idx]:
            x += dx; y += dy
            pts.append([round(x * kx + tx, 1), round(y * ky + ty, 1)])
        return pts[::-1] if idx < 0 else pts
    def _ring(arc_list):
        coords = []
        for i, idx in enumerate(arc_list):
            seg = _arc(idx)
            coords.extend(seg if i == 0 else seg[1:])
        if coords and coords[0] != coords[-1]:
            coords.append(coords[0])
        return coords
    def _geom_to_polys(geom):
        """Recursively collect polygon rings from any geometry type."""
        t = geom["type"]
        if t == "Polygon":
            return [[_ring(r) for r in geom["arcs"]]]
        if t == "MultiPolygon":
            return [[_ring(r) for r in poly] for poly in geom["arcs"]]
        if t == "GeometryCollection":
            result = []
            for g in geom.get("geometries", []):
                result.extend(_geom_to_polys(g))
            return result
        return []

    polygons = _geom_to_polys(topo["objects"]["land"])
    if not polygons:
        return "null"
    geo = {"type": "MultiPolygon", "coordinates": polygons}
    return json.dumps(geo, separators=(",", ":"))

land_geojson_str = _fetch_land_geojson()

# ---------------------------------------------------------------------------
# Chart 4: Choropleth — Global Mental Health Disorder Prevalence (2019)
# ---------------------------------------------------------------------------
_data_2019 = df_no_world[df_no_world["Year"] == 2019].copy()
_data_2019["All Disorders"] = _data_2019[disorder_cols].sum(axis=1)

_all_geo_cols = ["All Disorders"] + disorder_cols

# Country name → ISO 3166-1 numeric (world-atlas TopoJSON keyed by this)
_ISO_NUM = {
    "Afghanistan": 4,   "Albania": 8,       "Algeria": 12,      "American Samoa": 16,
    "Andorra": 20,      "Angola": 24,       "Antigua and Barbuda": 28, "Argentina": 32,
    "Armenia": 51,      "Australia": 36,    "Austria": 40,      "Azerbaijan": 31,
    "Bahamas": 44,      "Bahrain": 48,      "Bangladesh": 50,   "Barbados": 52,
    "Belarus": 112,     "Belgium": 56,      "Belize": 84,       "Benin": 204,
    "Bermuda": 60,      "Bhutan": 64,       "Bolivia": 68,      "Bosnia and Herzegovina": 70,
    "Botswana": 72,     "Brazil": 76,       "Brunei": 96,       "Bulgaria": 100,
    "Burkina Faso": 854,"Burundi": 108,     "Cambodia": 116,    "Cameroon": 120,
    "Canada": 124,      "Cape Verde": 132,  "Central African Republic": 140,
    "Chad": 148,        "Chile": 152,       "China": 156,       "Colombia": 170,
    "Comoros": 174,     "Congo": 178,       "Cook Islands": 184,"Costa Rica": 188,
    "Croatia": 191,     "Cuba": 192,        "Cyprus": 196,      "Denmark": 208,
    "Djibouti": 262,    "Dominica": 212,    "Dominican Republic": 214,
    "Ecuador": 218,     "Egypt": 818,       "El Salvador": 222, "Equatorial Guinea": 226,
    "Eritrea": 232,     "Estonia": 233,     "Eswatini": 748,    "Ethiopia": 231,
    "Fiji": 242,        "Finland": 246,     "France": 250,      "Gabon": 266,
    "Gambia": 270,      "Georgia": 268,     "Germany": 276,     "Ghana": 288,
    "Greece": 300,      "Greenland": 304,   "Grenada": 308,     "Guam": 316,
    "Guatemala": 320,   "Guinea": 324,      "Guinea-Bissau": 624,"Guyana": 328,
    "Haiti": 332,       "Honduras": 340,    "Hungary": 348,     "Iceland": 352,
    "India": 356,       "Indonesia": 360,   "Iran": 364,        "Iraq": 368,
    "Ireland": 372,     "Israel": 376,      "Italy": 380,       "Jamaica": 388,
    "Japan": 392,       "Jordan": 400,      "Kazakhstan": 398,  "Kenya": 404,
    "Kiribati": 296,    "Kuwait": 414,      "Kyrgyzstan": 417,  "Laos": 418,
    "Latvia": 428,      "Lebanon": 422,     "Lesotho": 426,     "Liberia": 430,
    "Libya": 434,       "Lithuania": 440,   "Luxembourg": 442,  "Madagascar": 450,
    "Malawi": 454,      "Malaysia": 458,    "Maldives": 462,    "Mali": 466,
    "Malta": 470,       "Marshall Islands": 584, "Mauritania": 478,
    "Mauritius": 480,   "Mexico": 484,      "Moldova": 498,     "Monaco": 492,
    "Mongolia": 496,    "Montenegro": 499,  "Morocco": 504,     "Mozambique": 508,
    "Myanmar": 104,     "Namibia": 516,     "Nauru": 520,       "Nepal": 524,
    "Netherlands": 528, "New Zealand": 554, "Nicaragua": 558,   "Niger": 562,
    "Nigeria": 566,     "North Korea": 408, "North Macedonia": 807,
    "Northern Mariana Islands": 580, "Norway": 578, "Oman": 512,
    "Pakistan": 586,    "Palau": 585,       "Palestine": 275,   "Panama": 591,
    "Papua New Guinea": 598, "Paraguay": 600, "Peru": 604,      "Philippines": 608,
    "Poland": 616,      "Portugal": 620,    "Puerto Rico": 630, "Qatar": 634,
    "Romania": 642,     "Russia": 643,      "Rwanda": 646,
    "Saint Kitts and Nevis": 659, "Saint Lucia": 662,
    "Saint Vincent and the Grenadines": 670, "Samoa": 882,
    "San Marino": 674,  "Saudi Arabia": 682,"Senegal": 686,     "Serbia": 688,
    "Seychelles": 690,  "Sierra Leone": 694,"Singapore": 702,   "Slovakia": 703,
    "Slovenia": 705,    "Solomon Islands": 90, "Somalia": 706,  "South Africa": 710,
    "South Korea": 410, "South Sudan": 728, "Spain": 724,       "Sri Lanka": 144,
    "Sudan": 729,       "Suriname": 740,    "Sweden": 752,      "Switzerland": 756,
    "Syria": 760,       "Taiwan": 158,      "Tajikistan": 762,  "Tanzania": 834,
    "Thailand": 764,    "Togo": 768,        "Tonga": 776,       "Trinidad and Tobago": 780,
    "Tunisia": 788,     "Turkey": 792,      "Turkmenistan": 795,"Tuvalu": 798,
    "Uganda": 800,      "Ukraine": 804,     "United Arab Emirates": 784,
    "United Kingdom": 826, "United States": 840, "Uruguay": 858,"Uzbekistan": 860,
    "Vanuatu": 548,     "Venezuela": 862,   "Vietnam": 704,     "Yemen": 887,
    "Zambia": 894,      "Zimbabwe": 716,
}

_data_2019["iso_num"] = _data_2019["Country"].map(_ISO_NUM)
_geo_df = _data_2019.dropna(subset=["iso_num"]).copy()
_geo_df["iso_num"] = _geo_df["iso_num"].astype(int)
_geo_values = _geo_df[["Country", "iso_num"] + _all_geo_cols].to_dict(orient="records")

_TOPO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

_disorder_select = alt.param(
    name="disorder_select",
    value="All Disorders",
    bind=alt.binding_select(options=_all_geo_cols, name="Disorder: "),
)

# Grey base layer (all countries) + coloured foreground layer (data countries only)
_geo_bg = (
    alt.Chart(alt.topo_feature(_TOPO_URL, "countries"))
    .mark_geoshape(fill="#d4d4d4", stroke="#ffffff", strokeWidth=0.25)
)

_geo_fg = (
    alt.Chart(alt.topo_feature(_TOPO_URL, "countries"))
    .mark_geoshape(stroke="#ffffff", strokeWidth=0.25)
    .transform_lookup(
        lookup="id",
        from_=alt.LookupData(
            data=alt.InlineData(values=_geo_values),
            key="iso_num",
            fields=["Country"] + _all_geo_cols,
        )
    )
    .transform_fold(fold=_all_geo_cols, as_=["disorder", "value"])
    .transform_filter("datum.disorder === disorder_select")
    .transform_filter("datum.value != null")
    .encode(
        color=alt.Color(
            "value:Q",
            scale=alt.Scale(scheme="yelloworangered"),
            legend=alt.Legend(
                title="Prevalence (% of population)",
                orient="bottom",
                direction="horizontal",
                gradientLength=260,
                gradientThickness=12,
                **_LEGEND_STYLE,
            )
        ),
        tooltip=[
            alt.Tooltip("Country:N", title="Country"),
            alt.Tooltip("value:Q",   title="Prevalence (%)", format=".2f"),
        ]
    )
    .add_params(_disorder_select)
)

_geo_layered = (
    alt.layer(_geo_bg, _geo_fg)
    .project(type="naturalEarth1")
    .properties(width="container", height=420)
    .configure_view(strokeWidth=0, fill="transparent")
)

# Inline any named datasets created by configure_*
def _fix_named_datasets(spec):
    datasets = spec.get("datasets", {})
    if not datasets:
        return
    def _walk(node):
        if isinstance(node, dict):
            if "data" in node and isinstance(node["data"], dict):
                name = node["data"].get("name")
                if name and name in datasets:
                    node["data"] = {"values": datasets[name]}
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)
    _walk(spec)
    spec.pop("datasets", None)

_geo_dict = _geo_layered.to_dict()
_fix_named_datasets(_geo_dict)

# Make the gradient legend span the full chart width using a Vega signal
try:
    _geo_dict["layer"][1]["encoding"]["color"]["legend"]["gradientLength"] = {"signal": "width"}
except (KeyError, IndexError):
    pass

geo_spec = json.dumps(_geo_dict)

# ---------------------------------------------------------------------------
# Chart 5: Correlation — log(GDP) vs each disorder (Pearson r)
# ---------------------------------------------------------------------------
_agg_c = agg.copy()
_agg_c["log_GDP"] = np.log10(_agg_c["GDP"])
_corr_rows = []
for _col in disorder_cols:
    _r = float(_agg_c[["log_GDP", _col]].dropna().corr().iloc[0, 1])
    _corr_rows.append({"Disorder": _col, "Correlation": round(_r, 3)})
_corr_df = pd.DataFrame(_corr_rows)

_corr_chart = (
    alt.Chart(_corr_df)
    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
    .encode(
        x=alt.X("Correlation:Q",
                title="Pearson r  (log GDP vs. mean prevalence)",
                scale=alt.Scale(domain=[-0.1, 0.5]),
                axis=alt.Axis(grid=True, gridColor="#e9ecef", format=".2f",
                              labelFontSize=11, titleFontSize=12,
                              labelColor="#495057", titleColor="#343a40")),
        y=alt.Y("Disorder:N", sort="-x", title=None,
                axis=alt.Axis(labelFontSize=12, labelColor="#374151")),
        color=alt.condition(
            "datum.Correlation > 0",
            alt.value("#3b82f6"),
            alt.value("#ef5350")
        ),
        tooltip=[
            alt.Tooltip("Disorder:N",     title="Disorder"),
            alt.Tooltip("Correlation:Q",  title="Pearson r", format=".3f"),
        ],
    )
    .properties(width="container", height=190)
    .configure_view(strokeWidth=0)
)
_cd = _corr_chart.to_dict()
if "datasets" in _cd and "data" in _cd:
    _n = _cd["data"].get("name")
    if _n and _n in _cd["datasets"]:
        _cd["data"] = {"values": _cd["datasets"][_n]}
        del _cd["datasets"]
corr_spec = json.dumps(_cd)

# ---------------------------------------------------------------------------
# Chart 6: GDP-tier time trend — yearly avg prevalence, High vs Low GDP
# ---------------------------------------------------------------------------
_gdp_median  = agg["GDP"].median()
_tier_map    = {r["Country"]: ("High GDP" if r["GDP"] >= _gdp_median else "Low GDP")
                for _, r in agg.iterrows()}
_trend_src   = df_no_world.copy()
_trend_src["GDP Tier"] = _trend_src["Country"].map(_tier_map)
_trend_src   = _trend_src.dropna(subset=["GDP Tier"])
_trend_long  = (
    _trend_src.groupby(["Year", "GDP Tier"])[disorder_cols].mean()
    .reset_index()
    .melt(id_vars=["Year", "GDP Tier"], value_vars=disorder_cols,
          var_name="Disorder", value_name="Prevalence")
)

_trend_sel = alt.param(
    name="TrendDisorder",
    bind=alt.binding_select(options=disorder_cols, name="Disorder: "),
    value="Depressive Disorders",
)
_trend_chart = (
    alt.Chart(_trend_long)
    .mark_line(strokeWidth=2.5,
               point=alt.OverlayMarkDef(size=45, filled=True, strokeWidth=0))
    .transform_filter("datum.Disorder == TrendDisorder")
    .encode(
        x=alt.X("Year:O", title="Year",
                axis=alt.Axis(labelAngle=-30, labelFontSize=11, titleFontSize=12,
                              labelColor="#495057", titleColor="#343a40",
                              gridColor="#e9ecef")),
        y=alt.Y("Prevalence:Q", title="Mean Prevalence (% of population)",
                axis=alt.Axis(grid=True, gridColor="#e9ecef", labelFontSize=11,
                              titleFontSize=12, labelColor="#495057",
                              titleColor="#343a40")),
        color=alt.Color("GDP Tier:N",
                        scale=alt.Scale(domain=["High GDP", "Low GDP"],
                                        range=["#1e40af", "#dc2626"]),
                        legend=alt.Legend(title="GDP Tier", orient="top-left",
                                          symbolSize=100, symbolType="square",
                                          rowPadding=5, **_LEGEND_STYLE)),
        tooltip=[
            alt.Tooltip("Year:O",         title="Year"),
            alt.Tooltip("GDP Tier:N",     title="GDP Tier"),
            alt.Tooltip("Prevalence:Q",   title="Avg Prevalence (%)", format=".3f"),
        ],
    )
    .add_params(_trend_sel)
    .properties(width="container", height=340)
    .configure_view(strokeWidth=0, fill="transparent")
)
_td = _trend_chart.to_dict()
if "datasets" in _td and "data" in _td:
    _n = _td["data"].get("name")
    if _n and _n in _td["datasets"]:
        _td["data"] = {"values": _td["datasets"][_n]}
        del _td["datasets"]
gdp_trend_spec = json.dumps(_td)

# ---------------------------------------------------------------------------
# Chart 7: Regional average prevalence (all disorders, all years)
# ---------------------------------------------------------------------------
_region_long = (
    agg.copy()
    .melt(id_vars=["region_label"], value_vars=disorder_cols,
          var_name="Disorder", value_name="Prevalence")
    .groupby(["region_label", "Disorder"])["Prevalence"]
    .mean()
    .reset_index()
)

_region_sel = alt.param(
    name="RegionDisorder",
    value="Depressive Disorders",
)
REGION_ORDER = [
    "Americas", "Europe & Central Asia", "East Asia & Pacific",
    "Middle East & North Africa", "South Asia", "Sub-Saharan Africa", "Other",
]
_region_chart = (
    alt.Chart(_region_long)
    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
    .transform_filter("datum.Disorder == RegionDisorder")
    .encode(
        x=alt.X("Prevalence:Q", title="Mean Prevalence (% of population)",
                axis=alt.Axis(grid=True, gridColor="#e9ecef", labelFontSize=11,
                              titleFontSize=12, labelColor="#495057",
                              titleColor="#343a40")),
        y=alt.Y("region_label:N", title=None, sort="-x",
                axis=alt.Axis(labelFontSize=12, labelColor="#374151")),
        color=alt.Color("region_label:N",
                        scale=alt.Scale(
                            domain=list(REGION_LABELS.values()),
                            range=list(REGION_COLORS.values())),
                        legend=None),
        tooltip=[
            alt.Tooltip("region_label:N", title="Region"),
            alt.Tooltip("Prevalence:Q",   title="Mean Prevalence (%)", format=".3f"),
        ],
    )
    .add_params(_region_sel)
    .properties(width="container", height=240)
    .configure_view(strokeWidth=0)
)
_rd = _region_chart.to_dict()
if "datasets" in _rd and "data" in _rd:
    _n = _rd["data"].get("name")
    if _n and _n in _rd["datasets"]:
        _rd["data"] = {"values": _rd["datasets"][_n]}
        del _rd["datasets"]
region_avg_spec = json.dumps(_rd)

# ---------------------------------------------------------------------------
# Chart 7b: Regional average GDP (static vertical bar chart)
# ---------------------------------------------------------------------------
_region_gdp_agg = (
    agg.groupby("region_label")["GDP"]
    .mean()
    .reset_index()
    .rename(columns={"GDP": "Avg GDP"})
)

_region_gdp_chart = (
    alt.Chart(_region_gdp_agg)
    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
    .encode(
        x=alt.X("Avg GDP:Q", title="Mean GDP (millions USD)",
                axis=alt.Axis(grid=True, gridColor="#e9ecef", labelFontSize=11,
                              titleFontSize=12, labelColor="#495057",
                              titleColor="#343a40", format="~s")),
        y=alt.Y("region_label:N", title=None,
                sort=alt.EncodingSortField(field="Avg GDP", order="descending"),
                axis=alt.Axis(labelFontSize=12, labelColor="#374151")),
        color=alt.Color("region_label:N",
                        scale=alt.Scale(
                            domain=list(REGION_LABELS.values()),
                            range=list(REGION_COLORS.values())),
                        legend=None),
        tooltip=[
            alt.Tooltip("region_label:N", title="Region"),
            alt.Tooltip("Avg GDP:Q",      title="Mean GDP (M USD)", format=",.0f"),
        ],
    )
    .properties(width="container", height=240)
    .configure_view(strokeWidth=0)
)
_rgd = _region_gdp_chart.to_dict()
if "datasets" in _rgd and "data" in _rgd:
    _n = _rgd["data"].get("name")
    if _n and _n in _rgd["datasets"]:
        _rgd["data"] = {"values": _rgd["datasets"][_n]}
        del _rgd["datasets"]
region_gdp_spec = json.dumps(_rgd)

# ---------------------------------------------------------------------------
# Per-disorder top 10 for interactive D3 chart on mental health page
# ---------------------------------------------------------------------------
mh_top10_data = {}
for _col in disorder_cols:
    _top = (
        df_no_world.groupby("Country")[_col]
        .max()
        .reset_index()
        .nlargest(10, _col)
        .sort_values(_col, ascending=True)   # ascending → highest bar at top
        .rename(columns={_col: "value"})
    )
    mh_top10_data[_col] = _top[["Country", "value"]].to_dict(orient="records")

mh_top10_json = json.dumps(mh_top10_data)

# ---------------------------------------------------------------------------
# Chart: Top 10 Countries over Time — line chart with disorder dropdown
# ---------------------------------------------------------------------------
_top10_time_frames = []
for _col in disorder_cols:
    _top10_countries = (
        df_no_world.groupby("Country")[_col].mean()
        .nlargest(10).index.tolist()
    )
    _sub = (
        df_no_world[df_no_world["Country"].isin(_top10_countries)]
        [["Country", "Year", _col]].copy()
        .rename(columns={_col: "Prevalence"})
    )
    _sub["Disorder"] = _col
    _top10_time_frames.append(_sub)

_top10_time_df = pd.concat(_top10_time_frames, ignore_index=True)

# Build GDP rank labels (ranked across all countries with GDP data)
_gdp_ranks = (
    agg[["Country", "GDP"]].dropna()
    .copy()
    .assign(GDP_Rank=lambda d: d["GDP"].rank(ascending=False, method="min").astype(int),
            GDP_B=lambda d: (d["GDP"] / 1000).round(1))
    .assign(Country_Label=lambda d: d.apply(
        lambda r: f"{r['Country']} (#{int(r['GDP_Rank'])}, ${r['GDP_B']}B)", axis=1))
    [["Country", "Country_Label", "GDP_Rank", "GDP_B"]]
)
_top10_time_df = _top10_time_df.merge(_gdp_ranks, on="Country", how="left")
_top10_time_df["Country_Label"] = _top10_time_df["Country_Label"].fillna(
    _top10_time_df["Country"] + " (No GDP data)"
)
_top10_time_df["GDP_Rank"] = _top10_time_df["GDP_Rank"].fillna(0).astype(int)
_top10_time_df["GDP_B"] = _top10_time_df["GDP_B"].fillna(0.0)

_top10_time_sel = alt.param(
    name="disorder_type",
    value="Depressive Disorders",
    bind=alt.binding_select(options=disorder_cols, name="Disorder: "),
)

_top10_time_chart = (
    alt.Chart(_top10_time_df)
    .mark_line(strokeWidth=2)
    .transform_filter("datum.Disorder == disorder_type")
    .encode(
        x=alt.X("Year:O", title="Year",
                axis=alt.Axis(labelAngle=-30, labelFontSize=11,
                              labelColor="#495057", titleColor="#343a40")),
        y=alt.Y("Prevalence:Q", title="Percentage of Population (%)",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=True, gridColor="#e9ecef", labelFontSize=11,
                              titleFontSize=12, labelColor="#495057",
                              titleColor="#343a40", tickCount=40,
                              format=".1f")),
        color=alt.Color("Country_Label:N",
                        legend=alt.Legend(
                            title="Country (GDP Rank, Avg GDP)",
                            orient="right",
                            labelFontSize=11,
                            titleFontSize=12,
                            symbolSize=200,
                            symbolStrokeWidth=3,
                            rowPadding=5,
                            padding=10,
                            labelLimit=320,
                        )),
        tooltip=[
            alt.Tooltip("Country:N",    title="Country"),
            alt.Tooltip("GDP_Rank:Q",   title="World GDP Rank", format="d"),
            alt.Tooltip("GDP_B:Q",      title="Avg GDP (billions USD)", format=".1f"),
            alt.Tooltip("Year:O",       title="Year"),
            alt.Tooltip("Prevalence:Q", title="Prevalence (%)", format=".3f"),
        ],
    )
    .add_params(_top10_time_sel)
    .properties(width="container", height=400)
)

_top10_time_dict = _top10_time_chart.to_dict()
if "datasets" in _top10_time_dict and "data" in _top10_time_dict:
    _n = _top10_time_dict["data"].get("name")
    if _n and _n in _top10_time_dict["datasets"]:
        _top10_time_dict["data"] = {"values": _top10_time_dict["datasets"][_n]}
        del _top10_time_dict["datasets"]
top10_time_spec = json.dumps(_top10_time_dict)

# ---------------------------------------------------------------------------
# Chart: Country Disorder Trends — all 5 disorders for a user-selected country
# ---------------------------------------------------------------------------
_country_long = (
    df_no_world
    .melt(id_vars=["Country", "Year"], value_vars=disorder_cols,
          var_name="Disorder", value_name="Prevalence")
)

_country_gdp_lookup = (
    agg[["Country", "GDP"]].copy()
    .assign(GDP_B=lambda d: (d["GDP"] / 1000).round(1))
    .assign(GDP_Label=lambda d: d.apply(
        lambda r: f"Country GDP: ${r['GDP_B']}B" if pd.notna(r["GDP_B"]) else "Country GDP: No data",
        axis=1,
    ))
    [["Country", "GDP_Label"]]
)

_country_list = sorted(df_no_world["Country"].unique().tolist())

_country_sel = alt.param(
    name="country_select",
    value="United States",
    bind=alt.binding_select(options=_country_list, name="Country: "),
)

_country_line = (
    alt.Chart(alt.InlineData(values=_country_long.to_dict(orient="records")))
    .mark_line(strokeWidth=2.5)
    .transform_filter("datum.Country === country_select")
    .encode(
        x=alt.X("Year:O", title="Year",
                axis=alt.Axis(labelAngle=-30, labelFontSize=11,
                              labelColor="#495057", titleColor="#343a40")),
        y=alt.Y("Prevalence:Q", title="Prevalence (% of Population)",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(grid=True, gridColor="#e9ecef", labelFontSize=11,
                              titleFontSize=12, labelColor="#495057",
                              titleColor="#343a40", format=".2f")),
        color=alt.Color("Disorder:N",
                        scale=alt.Scale(domain=disorder_cols, range=DISORDER_COLOR_RANGE),
                        legend=alt.Legend(
                            orient="right",
                            labelFontSize=12,
                            titleFontSize=12,
                            symbolSize=200,
                            symbolStrokeWidth=3,
                            rowPadding=5,
                            padding=10,
                        )),
        tooltip=[
            alt.Tooltip("Disorder:N",   title="Disorder"),
            alt.Tooltip("Year:O",       title="Year"),
            alt.Tooltip("Prevalence:Q", title="Prevalence (%)", format=".3f"),
        ],
    )
    .add_params(_country_sel)
)

_country_gdp_text = (
    alt.Chart(alt.InlineData(values=_country_gdp_lookup.to_dict(orient="records")))
    .mark_text(align="right", baseline="top", fontSize=13,
               fontWeight="bold", color="#343a40", dx=-10, dy=10)
    .transform_filter("datum.Country === country_select")
    .encode(
        x=alt.value("width"),
        y=alt.value(0),
        text=alt.Text("GDP_Label:N"),
    )
)

_country_time_layered = (
    alt.layer(_country_line, _country_gdp_text)
    .properties(width="container", height=350)
)

_ctd = _country_time_layered.to_dict()
_fix_named_datasets(_ctd)
country_time_spec = json.dumps(_ctd)
