import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
import numpy as np

# load dataset
data = pd.read_csv('ds4200_final_data_clean.csv')

# filter for 2019 drop '-N/a' GDP rows
data['GDP'] = data['Country GDP (millions USD)'].str.replace(',','').str.split('(').str[0].str.strip()
data = data[(data['GDP'] != '—N/a') & (data['Country'] != 'World')]
data['GDP'] = data['GDP'].astype(float)

# get total mental disorder percentage a filter for 2019
data['Total Disease'] = data['Schizophrenia'] + data['Depressive Disorders'] + data['Anxiety Disorders'] + data['Bipolar Disorders'] + data['Eating Disorders']
df_2019 = data[data['Year'] == 2019][['Country', 'Total Disease']].copy()

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


merged = world.merge(df_2019, left_on='NAME', right_on='map_name', how='left')
missing = merged[merged['Total Disease'].isna()]['NAME'].tolist()


fig, ax = plt.subplots(1, 1, figsize=(16, 6))

merged.plot(column='Total Disease', ax=ax, legend=True,
    legend_kwds={
        'label': 'Total Mental Health Disorder Prevalence (Percent(%) of Population)',
        'orientation': 'horizontal',
        'shrink': 0.5,
        'pad': 0.05,},
    missing_kwds={'color': 'lightgrey', 'label': 'No Data'}, cmap='YlOrRd', edgecolor='black',
    linewidth=0.3,
)

ax.set_title('Global Distribution of Mental Health Disorder Prevalence in 2019')

ax.set_axis_off()
plt.tight_layout()

plt.show()
