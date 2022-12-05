"""
Code by Anne Urai, Leiden University, 2022
Run with ssm_env on Windows
"""

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

#% ===============================
# get data from Our World in Data: https://github.com/owid/co2-data
# codebook; https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv
data = pd.read_csv('https://nyc3.digitaloceanspaces.com/owid-public/data/co2/owid-co2-data.csv')
df_historic = data.loc[data.country == 'World', ['year', 'co2', 'cumulative_co2']]
df_historic['scenario'] = 0

# add different scenarios for emission reduction between 2020 and 2050
df_future_1 = pd.DataFrame({'year':np.arange(2020, 2100), 
                          'co2':np.zeros(80,),
                          'scenario': 1})
df_future_2 = pd.DataFrame({'year':np.arange(2020, 2100), 
                          'co2':np.ones(80,) * df_historic.co2.values[-1],
                          'scenario': 2})
df = pd.concat([df_historic, df_future_1, df_future_2]).reset_index()
print(data.head(n=10))

# todo: for each scenario, integrate to get the cumulative CO2

#% ===============================
# now plot some historic CO2

fig, ax = plt.subplots(2, 1, figsize=(8,8), 
                       sharex=True, sharey=False)
sns.lineplot(data=df, x='year', y='co2', hue='scenario', palette='colorblind',
             ax=ax[0]).set(xlim=[1750, 2100], 
                           ylabel='Yearly CO2 emissions',
                           xlabel='')
sns.lineplot(data=df, x='year', y='cumulative_co2', 
             ax=ax[1]).set(ylabel='Total CO2 in atmosphere', xlabel='')

# annotate
ax[0].annotate('Invention of steam engine', 
               xy=(1776, 100),  xycoords='data',
               xytext=(1776, 10000), textcoords='data',
               arrowprops=dict(facecolor='black', shrink=0.05),
               horizontalalignment='left', verticalalignment='top')
sns.despine(trim=True)
fig.savefig('carbon_budget.png')
