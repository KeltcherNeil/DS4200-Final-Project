import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RadioButtons
import geopandas as gpd
import numpy as np


data = pd.read_csv('ds4200_final_data.csv')

# drop '-N/a' GDP rows and get only 2019 rows
data['GDP'] = data['Country GDP (millions USD)'].str.replace(',','').str.split('(').str[0].str.strip()
data = data[(data['GDP'] != '—N/a') & (data['Country'] != 'World')]
data['GDP'] = data['GDP'].astype(float)

# compute total and filter for 2019
disorder_cols = ['Schizophrenia', 'Depressive Disorders', 'Anxiety Disorders', 'Bipolar Disorders', 'Eating Disorders']
data['All Disorders'] = data[disorder_cols].sum(axis=1)

df_2019 = data[data['Year'] == 2019][['Country'] + disorder_cols + ['All Disorders']].copy()

world = gpd.read_file('https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip')


countries = {
    'United States': 'United States of America',
    'Russia': 'Russia',
    'South Korea': 'South Korea',
    'North Korea': 'North Korea',
    'Congo': 'Dem. Rep. Congo',
    'Democratic Republic of Congo': 'Dem. Rep. Congo',
    'Central African Republic': 'Central African Rep.',
    'South Sudan': 'S. Sudan',
    'Dominican Republic': 'Dominican Rep.',
    'Bosnia and Herzegovina': 'Bosnia and Herz.',
    'Equatorial Guinea': 'Eq. Guinea',
    'Solomon Islands': 'Solomon Is.',
    'Eswatini': 'eSwatini',
}

df_2019['map_name'] = df_2019['Country'].replace(countries)

# merge all disorder columns into world
merged = world.merge(df_2019, left_on='NAME', right_on='map_name', how='left')

# disorder options for switch widget
disorder_options = ['All Disorders'] + disorder_cols


fig, ax = plt.subplots(1, 1, figsize=(16, 7))

plt.subplots_adjust(left=0.22, bottom=0.08)


sm = plt.cm.ScalarMappable(
    cmap='YlOrRd',
    norm=mcolors.Normalize(vmin=merged['All Disorders'].min(), vmax=merged['All Disorders'].max()),
)

sm._A = []

cbar = fig.colorbar(
    sm, ax=ax, orientation='horizontal', shrink=0.5, pad=0.05,

    label='All Disorders Prevalence (% of Population)',
)

def draw_map(disorder_name):
    ax.clear()

    col = disorder_name
    vmin = merged[col].min()
    vmax = merged[col].max()

    merged.plot( column=col, ax=ax,
        legend=False,
        missing_kwds={'color': 'lightgrey', 'label': 'No Data'},
        cmap='YlOrRd',
        edgecolor='black',
        linewidth=0.3,
        vmin=vmin,
        vmax=vmax,
    )


    sm.set_norm(mcolors.Normalize(vmin=vmin, vmax=vmax))
    cbar.update_normal(sm)
    cbar.set_label(f'{disorder_name} Prevalence (% of Population)')

    ax.set_title(f'Global Distribution of {disorder_name} Prevalence in 2019')
    ax.set_axis_off()

    fig.canvas.draw_idle()


draw_map('All Disorders')

# radio button select
radio_ax = fig.add_axes([0.02, 0.25, 0.17, 0.45], facecolor='#f7f7f7')

radio_ax.set_title('Disorder Type', fontsize=10, fontweight='bold', pad=8)
radio = RadioButtons(radio_ax, disorder_options, active=0, activecolor='#d62728')

def on_select(label):

    draw_map(label)

radio.on_clicked(on_select)

plt.show()
