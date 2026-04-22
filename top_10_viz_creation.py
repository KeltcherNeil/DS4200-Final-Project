import altair as alt
import pandas as pd

df = pd.read_csv('ds4200_final_data.csv')

disorders = ['Schizophrenia', 'Depressive Disorders', 'Anxiety Disorders',
             'Bipolar Disorders', 'Eating Disorders']

def get_top10(df, item):
    grouped = df.groupby('Country')[item]
    change = (grouped.max() - grouped.min()) / grouped.sum()
    return change.nlargest(10).index.tolist()

frames = []
for disorder in disorders:
    top10 = get_top10(df, disorder)
    subset = df[df['Country'].isin(top10)].copy()
    subset['rank_by'] = disorder
    frames.append(subset)

combined = pd.concat(frames, ignore_index=True)

rank_dropdown = alt.binding_select(options=disorders, name='Rank top 10 by: ')
rank_select = alt.selection_point(
    fields=['rank_by'],
    bind=rank_dropdown,
    value='Depressive Disorders'
)

chart = alt.Chart(combined).mark_line().encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Depressive Disorders:Q', title='Percentage of Population (%)'),
    color=alt.Color('Country:N', legend=alt.Legend(orient='right')),
    tooltip=['Country:N', 'Year:O',
             alt.Tooltip('Depressive Disorders:Q', format='.3f')]
).transform_filter(
    rank_select
).add_params(
    rank_select
).properties(
    width=700,
    height=400,
    title='Mental Health Disorders — Top 10 Countries by Change Over Time'
)

chart.save('chart.html')