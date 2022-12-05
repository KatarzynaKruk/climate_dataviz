"""
Code by Anne Urai, Leiden University, 2022
Run with ssm_env on Windows
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#% ===============================
# get data from Our World in Data: https://github.com/owid/co2-data
# codebook; https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv
data = pd.read_csv('https://nyc3.digitaloceanspaces.com/owid-public/data/co2/owid-co2-data.csv')
df = data.loc[data.country == 'World', ['year', 'co2', 'cumulative_co2']]

# to do: add different scenarios for emission reduction between 2020 and 2050

print(data.head(n=10))

#% ===============================
# now plot some historic CO2

fig, ax = plt.subplots(2, 1, figsize=(8,8), 
                       sharex=True, sharey=False)
sns.lineplot(data=df, x='year', y='co2', ax=ax[0]).set(xlim=[1750, 2022], 
                                                       ylabel='Yearly CO2 emissions',
                                                       xlabel='')
sns.lineplot(data=df, x='year', y='cumulative_co2', 
             ax=ax[1]).set(ylabel='Total CO2 in atmosphere', xlabel='')
ax[0].annotate('Invention of steam engine', 
               xy=(1776, 100),  xycoords='data',
               xytext=(1776, 10000), textcoords='data',
               arrowprops=dict(facecolor='black', shrink=0.05),
               horizontalalignment='left', verticalalignment='top')
sns.despine(trim=True)
plt.show()
plt.savefig('carbon_budget.png')
