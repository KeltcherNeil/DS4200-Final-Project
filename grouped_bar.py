import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv('ds4200_final_data.csv')

# grouped bar chart

# clean gdp data and convert to float
data['GDP'] = data['Country GDP (millions USD)'].str.replace(',','').str.split('(').str[0].str.strip()
data = data[(data['GDP'] != '—N/a') & (data['Country'] != 'World')]
data['GDP'] = data['GDP'].astype(float)

# get top and bottom 10 gdp countries
top_ten = data[data['Year']==2019].nlargest(10, 'GDP')
bottom_ten = data[data['Year']==2019].nsmallest(10, 'GDP')


x_ticks = np.arange(10)

# create two framed grouped bar visualization
width = 0.15

fig, (left, right) = plt.subplots(1, 2, figsize= (16, 6))

left.bar(x_ticks - 2 * width, top_ten['Schizophrenia'], width, label='Schizophrenia')
left.bar(x_ticks - width, top_ten['Depressive Disorders'], width, label='Depression')
left.bar(x_ticks, top_ten['Anxiety Disorders'], width, label='Anxiety')
left.bar(x_ticks + width, top_ten['Bipolar Disorders'], width, label='Bipolar')
left.bar(x_ticks + 2 * width, top_ten['Eating Disorders'], width, label='Eating')

left.set_xticks(x_ticks)
left.set_xticklabels(top_ten['Country'], rotation=45, ha='right')
left.set_ylabel("Percent(%) of Population")
left.set_title('Mental Health Disorder Prevalence in the Top 10 Highest GDP Countries (2019)')

right.bar(x_ticks - 2 * width, bottom_ten['Schizophrenia'], width, label='Schizophrenia')
right.bar(x_ticks - width, bottom_ten['Depressive Disorders'], width, label='Depression')
right.bar(x_ticks, bottom_ten['Anxiety Disorders'], width, label='Anxiety')
right.bar(x_ticks + width, bottom_ten['Bipolar Disorders'], width, label='Bipolar')
right.bar(x_ticks + 2 * width, bottom_ten['Eating Disorders'], width, label='Eating')

right.set_xticks(x_ticks)
right.set_xticklabels(bottom_ten['Country'], rotation=45, ha='right')
right.set_ylabel("Percent(%) of Population")
right.set_title('Mental Health Disorder Prevalence in the Bottom 10 Lowest GDP Countries (2019)')

fig.legend(labels=['Schizophrenia', 'Depression', 'Anxiety', 'Bipolar', 'Eating'],
           loc='lower center', ncol=5, bbox_to_anchor=(0.5, -0.05))

plt.tight_layout()

plt.show()
