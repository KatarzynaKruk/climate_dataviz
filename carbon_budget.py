"""
Code by Anne Urai, Leiden University, 2022
Run with ssm_env on Windows

This script visualizes the carbon budget, and shows how different emission reduction scenarios lead to different temperature changes.
See the repo's README for data sources.

"""

# %%
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as stats

def seaborn_style():
    """
    Set seaborn style for plotting figures
    """
    sns.set(style="ticks", context="paper",
            font="Arial",
            rc={"font.size": 9,
                "axes.titlesize": 9,
                "axes.labelsize": 9,
                "lines.linewidth": 1,
                "xtick.labelsize": 7,
                "ytick.labelsize": 7,
                "savefig.transparent": False,
                "savefig.dpi": 300,
                "xtick.major.size": 2.5,
                "ytick.major.size": 2.5,
                "xtick.minor.size": 2,
                "ytick.minor.size": 2,
                })
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

seaborn_style()

# %% ===============================
# get data https://doi.org/10.5194/essd-14-4811-2022
df_historic = pd.read_excel('https://globalcarbonbudgetdata.org/downloads/latest-data/Global_Carbon_Budget_2022v1.0.xlsx',
                    sheet_name='Historical Budget', header=15, usecols='A:B')

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

# and another set, but with net-zero only in 2075
beta_params = [ [3,3], [5,2]] # fast, medium, procrastinate
for scen_idx, beta_param in enumerate(beta_params):
    x = np.linspace(0, 1, 54)
    this_cdf = df_historic.co2.values[-1] * (-stats.beta.cdf(x,
                beta_param[0], beta_param[1]) + 1)

    # add to dataframe
    df_future = pd.concat([df_historic, 
        pd.DataFrame({'year':np.arange(2022, 2076), 'co2':this_cdf}),
        pd.DataFrame({'year':np.arange(2075, 2101), 'co2':np.zeros(26,)}
        )])
    df_future['scenario'] = scen_idx + 4
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
# map ppm to temperature change
# first way: \Delta T = 0.8 * 5.35 * ln(CO2/CO2_0) 
baseline = df.loc[(df.year > 1951) & (df.year < 1980), 'ppm_co2_scenarios'].mean() # NASA GIS baseline years
df['temp_scenarios'] =  0.8 * 5.35 * np.log(df['ppm_co2_scenarios'] / baseline)

# %% ===============================
# visualize all of these
cmap = 'copper'

fig, ax = plt.subplots(3, 1, figsize=(6, 9), 
                       sharex=True, sharey=False)
sns.lineplot(data=df, x='year', y='co2', hue='scenario', 
            palette=cmap,
            legend=False,
            ax=ax[0]).set(xlim=[1900, 2100], ylim=[0, 40],
                           ylabel='Yearly CO2 emissions\n(GtCO2)',
                           xlabel='')
# sns.lineplot(data=df, x='year', y='cumulative_co2_scenarios', 
#             hue='scenario', 
#             palette=cmap, legend=False,
#             ax=ax[1]).set(ylabel='Total Gt CO2\nadded to atmosphere', xlabel='')

# convert to ppm in atmosphere
sns.lineplot(data=df, x='year', y='ppm_co2_scenarios', 
            hue='scenario', 
            palette=cmap, legend=False,
            ax=ax[1]).set(ylabel='Concentration \natmospheric CO2 (ppm)', xlabel='')
sns.lineplot(data=keeling, x='year', y='average',  # overlay Keeling curve onto ppm
            color='grey', legend=False,
            ax=ax[1])

# convert to temperature
sns.lineplot(data=df, x='year', y='temp_scenarios', 
            hue='scenario', 
            palette=cmap, legend=False, 
            ax=ax[2])
sns.lineplot(data=temp_df, x='year', y='value', 
            color='grey', legend=False,
            ax=ax[2]).set(ylabel='Temperature $(\Delta ^{\circ}$C)', xlabel='', ylim=[-0.9, 2.2])

# layout
sns.despine(trim=True)
fig.suptitle('Global CO2 emissions and climate change', x=0.5, y=0.9)
fig.supxlabel('By Anne Urai | Data: NASA, NOAA, Global Carbon Project', 
               x=0.9, y=0.05, ha='right', color='lightgrey')
fig.savefig('figures/carbon_emissions_global.png',
            facecolor='white', transparent=False)
fig.savefig('figures/carbon_emissions_global.svg',
            facecolor='white', transparent=False)

# %% ===============================
# map onto budgets, from IPCC WG1 AR6 - Table TS.3
temps = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
budget = {17: [900, 1200, 1450, 1750, 2000, 2300],
        33:[650, 850, 1050, 1250, 1450, 1700],
        50:[500, 650, 850, 1000, 1200, 1350],
        67:[400, 550, 700, 850, 1000, 1150],
        83:[300, 400, 550, 650, 800, 900]}

# for each scenario, compute cumulative emissions from 2020 onwards
budgets = df[df.year >= 2020].groupby('scenario')['co2'].sum().reset_index()

# from this, estimate linear curves
for prct in [17, 33, 50, 67, 83]:
    budget_model = np.polyfit(budget[prct], temps, 1)
    budgets[f'temp_{prct}p'] = budgets['co2'] * budget_model[0] + budget_model[1]

budgets_df = pd.melt(budgets, id_vars=['scenario', 'co2'], value_vars=[f'temp_{prct}p' for prct in [17, 33, 50, 67, 83]])
budgets_df['prct'] = budgets_df['variable'].str.extract('(\d+)')

# %%
fig, ax = plt.subplots(1, 2, figsize=(8, 4))

# once for the legend, once overlaid for the scenario colors
sns.scatterplot(data=budgets_df, x='co2', y='value', 
                ax=ax[0], size='prct', legend='full')
sns.scatterplot(data=budgets_df, x='co2', y='value', hue='scenario', palette=cmap,
                ax=ax[0], size='prct', legend=False)

# improve the legend
handles, labels = ax[0].get_legend_handles_labels()
order = [4,3,2,1,0]
ax[0].legend([handles[idx] for idx in order], [labels[idx] for idx in order],
            title='Chance (%)', fancybox=True) 

ax[0].set(ylabel='Temperature $(\Delta ^{\circ}$C) exceeded', ylim=[1, 2.5],
        xlabel='Additional CO2 emissions from 2020 (GtCO2)', xlim=[0, 1500], 
        title='Carbon budgets')
sns.move_legend(ax[0], loc='lower right', bbox_to_anchor=(1.4, 0.6), ncol=1, frameon=True)

sns.despine(trim=True)
#x[0].legend(loc='center left', bbox_to_anchor=(1.25, 0.5), ncol=1)
ax[1].set_axis_off()

fig.supxlabel('By Anne Urai | Data: IPCC', x=0.3, y=-0.05, ha='right', color='lightgrey')
fig.savefig('figures/carbon_budgets.png',
            facecolor='white', transparent=False)
fig.savefig('figures/carbon_budgets.svg',
            facecolor='white', transparent=False)

# %%
