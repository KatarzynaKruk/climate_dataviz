"""
Code by Anne Urai, Leiden University, 2022
Run with ssm_env on Windows
"""

# %%
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# %% ===============================
# get data from Our World in Data: https://github.com/owid/co2-data
# codebook; https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv
data = pd.read_csv('https://nyc3.digitaloceanspaces.com/owid-public/data/co2/owid-co2-data.csv',
                        usecols= ['year', 'co2', 'country'])
# todo Kasia: try for different places in the world. at the end, can generate for each (269 places)
place = 'World'
df_historic = data.loc[data.country == place, :]

# %% add different scenarios for emission reduction between 2020 and 2050
# use Beta function to model decreasing emissions at different rates
beta_params = [ [2,5], [3,3], [5,2]] # fast, medium, procrastinate
scenario_list = []
for scen_idx, beta_param in enumerate(beta_params):
    x = np.linspace(0, 1, 28)
    this_cdf = df_historic.co2.values[-1] * (-stats.beta.cdf(x,
                beta_param[0], beta_param[1]) + 1)

    # add to dataframe
    df_future = pd.concat([df_historic, 
        pd.DataFrame({'year':np.arange(2023, 2051), 'co2':this_cdf}),
        pd.DataFrame({'year':np.arange(2050, 2101), 'co2':np.zeros(51,)}
        )])
    df_future['scenario'] = scen_idx + 1
    scenario_list.append(df_future)

df = pd.concat(scenario_list).reset_index()
# %%

# for each scenario, integrate to get the cumulative CO2
df['cumulative_co2_scenarios'] = df.groupby(['scenario'])['co2'].cumsum()
# remove duplicate of all the scenarios that lie in the past
df.loc[df.year < df_historic.year.max()+1, 'scenario'] = 0
df.drop_duplicates(inplace=True)

# %% now plot some historic CO2

cmap = 'viridis' # todo kasia: pick a colormap

fig, ax = plt.subplots(2, 1, figsize=(8,8), 
                       sharex=True, sharey=False)
sns.lineplot(data=df, x='year', y='co2', hue='scenario', 
            palette=cmap,
            legend=False,
            ax=ax[0]).set(xlim=[1900, 2100], #ylim=[0, 50000],
                           ylabel='Yearly CO2 emissions',
                           xlabel='')
sns.lineplot(data=df, x='year', y='cumulative_co2_scenarios', 
            hue='scenario', 
            palette=cmap, legend=False,
            ax=ax[1]).set(ylabel='Total CO2 in atmosphere', xlabel='')

# annotate
ax[0].annotate('Invention of steam engine', 
               xy=(1776, 100),  xycoords='data',
               xytext=(1776, 10000), textcoords='data',
               arrowprops=dict(facecolor='black', shrink=0.05),
               horizontalalignment='left', verticalalignment='top')
ax[0].annotate('Today', 
               xy=(2023, df.loc[df.year == 2023, 'co2'].max()*1.05),  xycoords='data',
               xytext=(2023, df.loc[df.year == 2023, 'co2'].max()*1.3), textcoords='data',
               arrowprops=dict(facecolor='black', shrink=0.05),
               horizontalalignment='center', verticalalignment='top')
ax[0].annotate('Net-zero', 
               xy=(2050, df.loc[df.year == 2049, 'co2'].max()*1.05),  xycoords='data',
               xytext=(2050, df.loc[df.year == 2049, 'co2'].max()*20), textcoords='data',
               arrowprops=dict(facecolor='black', shrink=0.1),
               horizontalalignment='left', verticalalignment='top')
sns.despine(trim=True)
fig.suptitle('CO2 emissions in: %s'%place)
fig.savefig('figures/carbon_budget_%s.png'%place,
            facecolor='white', transparent=False)

# %%
