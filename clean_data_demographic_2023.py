import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Read CSV
df = pd.read_csv('./data_2023/Ohio_District_all_2023.csv')

# Step 1: Melt the dataframe to long format
df_long = pd.melt(
    df, 
    id_vars=['Title'], 
    var_name='CD119FP', 
    value_name='Value'
)

# Step 2: Pivot so that Title values become columns
df_wide = df_long.pivot(
    index='CD119FP', 
    columns='Title', 
    values='Value'
).reset_index()

df_wide['CD119FP'] = df_wide['CD119FP'].str.extract(r'(\d+)').astype(int)
for col in df_wide.columns.difference(['CD119FP']):
    df_wide[col] = pd.to_numeric(df_wide[col].astype(str).str.replace(',', ''), errors='coerce')

# Sex, poverty, & education variables
df_wide['Women'] = (df_wide['Female']) / (df_wide['Female'] + df_wide['Male']) * 100
df_wide['Did not finish high school'] = 100 - df_wide['Percent high school graduate or higher']
df_wide.rename(columns={'Poverty Rate': 'In Poverty', 'Percent bachelor\'s degree or higher': 'Bachelors or more'},
                inplace=True)
df_wide.drop(['Female', 'Male', 'Percent high school graduate or higher',
              'Less than 9th grade', 'Total Population 25 years and over', '9th to 12th grade, no diploma'], axis=1, inplace=True)

# Age variables
# Isolate Age variables to calculate age
age_df = df_wide[['CD119FP', 'Total population', 'Under 5 years','5 to 9 years', '10 to 14 years', '15 to 19 years', 
       '20 to 24 years', '25 to 34 years', '35 to 44 years', '45 to 54 years',
       '55 to 59 years', '60 to 64 years', '18 years and over', '65 years and over']].copy()
age_df['18-19'] = age_df['Under 5 years'] + age_df['5 to 9 years'] + age_df['10 to 14 years'] + age_df['15 to 19 years'] - age_df['Total population'] + age_df['18 years and over']
age_df['Voting Population'] = age_df['18 years and over']
age_df['18-44'] = (age_df['18-19'] + age_df['20 to 24 years'] + age_df['25 to 34 years'] + age_df['35 to 44 years']) / age_df['Voting Population'] * 100
age_df['45-64'] = (age_df['45 to 54 years'] + age_df['55 to 59 years'] + age_df['60 to 64 years']) / age_df['Voting Population'] * 100
age_df['65 and older'] = age_df['65 years and over'] / age_df['Voting Population'] * 100
age_df = age_df[['CD119FP', '18-44', '45-64', '65 and older']]

# Race variables
race_df = df_wide[['CD119FP', 'Total population', 'White', 'Black or African American',
                   'Asian', 'Hispanic or Latino (of any race)']].copy()
race_df.rename(columns={'Black or African American': 'Black', 'Hispanic or Latino (of any race)': 'Hispanic'},
                inplace=True)
race_df['White'] = race_df['White'] / race_df['Total population'] * 100
race_df['Black'] = race_df['Black'] / race_df['Total population'] * 100
race_df['Asian'] = race_df['Asian'] / race_df['Total population'] * 100
race_df['Hispanic'] = race_df['Hispanic'] / race_df['Total population'] * 100

# Merge final dataset
cd = df_wide.copy()
# Drop race & age columns
cd.drop(['Under 5 years','5 to 9 years', '10 to 14 years', '15 to 19 years', 
       '20 to 24 years', '25 to 34 years', '35 to 44 years', '45 to 54 years',
       '55 to 59 years', '60 to 64 years', '18 years and over', '65 years and over',
       'White', 'Black or African American','Asian', 'Hispanic or Latino (of any race)'],axis=1, inplace=True)
# Merge back age df
cd = cd.merge(
    age_df[['CD119FP', '18-44', '45-64', '65 and older']],
    on='CD119FP',
    how='left'
)
# Merge back race df
cd = cd.merge(
    race_df[['CD119FP', 'White', 'Black', 'Asian', 'Hispanic']],
    on='CD119FP',
    how='left'
)
cd['CD119'] = 'Ohio ' + cd['CD119FP'].astype(str).str.zfill(2)

# Final columns included are same as 2018 dataset
cd = cd[['CD119', '18-44', '45-64', '65 and older',
       'Women', 'In Poverty', 'Did not finish high school',
       'Bachelors or more', 'White', 'Black', 'Asian', 'Hispanic']]
cd = cd.round(1)

# Further choose columns
# cd['Non-white'] = 100 - cd['White']
# cd['45 and older'] = cd['65 and older'] + cd['45-64']
# cd = cd[['CD119', 'Bachelors or more', '45 and older', 'In Poverty', 'Non-white', ]]

cd.to_csv('./data_2023/cd_2023.csv', index=False)
