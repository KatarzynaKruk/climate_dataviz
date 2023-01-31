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
# get data https://doi.org/10.5194/essd-14-4811-2022
df_historic = pd.read_excel('https://globalcarbonbudgetdata.org/downloads/latest-data/Global_Carbon_Budget_2022v1.0.xlsx',
                    sheet_name='Historical Budget', header=15)

# All values in billion tonnes of carbon per year (GtC/yr), for the globe. 
# For values in billion tonnes of carbon dioxide (CO2) per year, multiply the numbers below by 3.664.
df_historic['co2'] = df_historic['fossil emissions excluding carbonation'] * 3.664
df_historic['year'] = df_historic['Year'] #rename to lowercase

# %% ===============================
# sanity check: overlay Keeling curve
keeling = pd.read_csv('https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv', header=55)
keeling['year'] = keeling.year + (keeling.month - 1) / 12

# %% ===============================
# temperature records from NASA
temp = pd.read_csv('https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv', header=1)
temp2 = temp.rename(columns={"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, 
                            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12})
temp_df = pd.melt(temp2, id_vars='Year', value_vars=[*range(1, 13, 1)])
temp_df['year'] = temp_df.Year + (temp_df.variable - 1) / 12
temp_df = temp_df.sort_values(by=['Year'])

# %% ===============================
# add different scenarios for emission reduction between 2020 and 2050
# use Beta function to model decreasing emissions at different rates

beta_params = [ [2,5], [3,3], [5,2]] # fast, medium, procrastinate
scenario_list = []
for scen_idx, beta_param in enumerate(beta_params):
    x = np.linspace(0, 1, 29)
    this_cdf = df_historic.co2.values[-1] * (-stats.beta.cdf(x,
                beta_param[0], beta_param[1]) + 1)

    # add to dataframe
    df_future = pd.concat([df_historic, 
        pd.DataFrame({'year':np.arange(2022, 2051), 'co2':this_cdf}),
        pd.DataFrame({'year':np.arange(2050, 2101), 'co2':np.zeros(51,)}
        )])
    df_future['scenario'] = scen_idx + 1
    scenario_list.append(df_future)

df = pd.concat(scenario_list).reset_index()
# %% ===============================
# for each scenario, integrate to get the cumulative CO2
df['cumulative_co2_scenarios'] = df.groupby(['scenario'])['co2'].cumsum()
# remove duplicate of all the scenarios that lie in the past
df.loc[df.year < df_historic.year.max()+1, 'scenario'] = 0
df.drop_duplicates(inplace=True)

# hack: convert cumulative CO2 to ppm in atmosphere using a simple linear conversion (by eye, mapping onto Keeling curve).
# the better way to do this would be to take land and ocean sinks into account, but this is a first approximation.
df['ppm_co2_scenarios'] = df['cumulative_co2_scenarios'] / 15.5 + 300

# %% ===============================
# Equilibrium Climate Sensitivity (ECS) is the temperature change that would occur if the atmospheric CO2 concentration were doubled
#df['temp_scenarios'] = 

# %% ===============================
# visualize all of these
cmap = 'viridis' # can change the colors in powerpoint

fig, ax = plt.subplots(4, 1, figsize=(7, 12), 
                       sharex=True, sharey=False)
sns.lineplot(data=df, x='year', y='co2', hue='scenario', 
            palette=cmap,
            legend=False,
            ax=ax[0]).set(xlim=[1900, 2100], ylim=[0, 40],
                           ylabel='Yearly CO2 emissions\n(GtCO2)',
                           xlabel='')
sns.lineplot(data=df, x='year', y='cumulative_co2_scenarios', 
            hue='scenario', 
            palette=cmap, legend=False,
            ax=ax[1]).set(ylabel='Total Gt CO2\nadded to atmosphere', xlabel='')

# convert to ppm in atmosphere
sns.lineplot(data=df, x='year', y='ppm_co2_scenarios', 
            hue='scenario', 
            palette=cmap, legend=False,
            ax=ax[2]).set(ylabel='Concentration \natmospheric CO2 (ppm)', xlabel='')
sns.lineplot(data=keeling, x='year', y='average',  # overlay Keeling curve onto ppm
            color='grey', legend=False,
            ax=ax[2])

# convert to temperature
sns.lineplot(data=temp_df, x='year', y='value', 
            color='grey', legend=False,
            ax=ax[3]).set(ylabel='Temperature $(\Delta ^{\circ}$C)', xlabel='', ylim=[-0.9, 2.2],)

# # annotate
# ax[0].annotate('Invention of steam engine', 
#                xy=(1776, 100),  xycoords='data',
#                xytext=(1776, 10000), textcoords='data',
#                arrowprops=dict(facecolor='black', shrink=0.05),
#                horizontalalignment='left', verticalalignment='top')
# ax[0].annotate('Today', 
#                xy=(2023, df.loc[df.year == 2023, 'co2'].max()*1.05),  xycoords='data',
#                xytext=(2023, df.loc[df.year == 2023, 'co2'].max()*1.3), textcoords='data',
#                arrowprops=dict(facecolor='black', shrink=0.05),
#                horizontalalignment='center', verticalalignment='top')
# ax[0].annotate('Net-zero', 
#                xy=(2050, df.loc[df.year == 2049, 'co2'].max()*1.05),  xycoords='data',
#                xytext=(2050, df.loc[df.year == 2049, 'co2'].max()*20), textcoords='data',
#                arrowprops=dict(facecolor='black', shrink=0.1),
#                horizontalalignment='left', verticalalignment='top')

# layout
sns.despine(trim=True)
fig.suptitle('Global CO2 emissions and climate change')
fig.savefig('figures/carbon_budget_global.png',
            facecolor='white', transparent=False)
fig.savefig('figures/carbon_budget_global.svg',
            facecolor='white', transparent=False)

# %%
