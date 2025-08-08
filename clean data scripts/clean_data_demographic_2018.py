# Load packages
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import zipfile
import os

# Function for cleaning data
def clean_cd_data(file_path, rename_dict, columns):
    #Read file
    data = pd.read_csv(file_path,
                          header=2,
                          skiprows=[3,4])
    #Rename columns
    data = data.rename(columns=rename_dict)
    #Filter out other states data
    states_list = ['Ohio', 'Indiana', 'Michigan', 'Pennsylvania', 'Wisconsin', 'Missouri']
    data = data[data['State name'].isin(states_list)]
    #Specify columns
    data = data[columns]
    #Add column for join
    data['CD116FP'] = data['Congressional district'].astype(int)
    return data

# Get new voter turnout data
turnout_file = "./data_2018/demographic_data/voter_turnout_2018.csv"
turnout_dict = {'Voting rate3': 'Voting rate'}
turnout_columns = ['State name', 'Congressional district', 'Voting rate']
voter_turnout = clean_cd_data(turnout_file, turnout_dict,turnout_columns)

# Age data
age_cd_file = "./data_2018/demographic_data/table02a_age_2018.csv"
age_cd_dict = {'Unnamed: 8': '18-29',
    'Unnamed: 12': '30-44',
    'Unnamed: 16': '45-64',
    'Unnamed: 20': '65 and older'}
age_cd_columns = ['State name', 'Congressional district', '18-29', '30-44', '45-64', '65 and older']
age_cd_gdf = clean_cd_data(age_cd_file, age_cd_dict, age_cd_columns)

# Sex & Poverty data
sex_poverty_cd_file = "./data_2018/demographic_data/table02b_sex_poverty_2018.csv"
sex_poverty_cd_dict = {'Unnamed: 8': 'Men',
    'Unnamed: 12': 'Women',
    'Unnamed: 18': 'In Poverty'}
sex_poverty_cd_columns = ['State name', 'Congressional district', 'Men', 'Women', 'In Poverty']
sex_poverty_cd_gdf = clean_cd_data(sex_poverty_cd_file, sex_poverty_cd_dict, sex_poverty_cd_columns)

# Education data
education_cd_file = "./data_2018/demographic_data/table02c_education_2018.csv"
education_cd_dict = {'Unnamed: 8': 'Less than 9th grade',
    'Unnamed: 12': '9th to 12 Grade, no diploma',
    'Unnamed: 36': 'High school or more',
    'Unnamed: 40': 'Bachelors or more'}
education_cd_columns = ['State name', 'Congressional district', 'Less than 9th grade', '9th to 12 Grade, no diploma', 'High school or more', 'Bachelors or more']
education_cd_gdf = clean_cd_data(education_cd_file, education_cd_dict, education_cd_columns)
# Making new column combining those that did not finish high school
education_cd_gdf['Did not finish high school'] = (
    education_cd_gdf['Less than 9th grade'] + education_cd_gdf['9th to 12 Grade, no diploma']
)
education_cd_gdf = education_cd_gdf.drop(
    ['Less than 9th grade', '9th to 12 Grade, no diploma'],
    axis=1
)

# Race data
race_cd_file = "./data_2018/demographic_data/table02d_race_2018.csv"
race_cd_dict = {'Unnamed: 8': 'White',
    'Unnamed: 12': 'Black',
    'Unnamed: 16': 'Asian',
    'Unnamed: 36': 'Hispanic'}
race_cd_columns = ['State name', 'Congressional district', 'White', 'Black', 'Asian', 'Hispanic']
race_cd_gdf = clean_cd_data(race_cd_file, race_cd_dict, race_cd_columns)
# Make sure data is numerical
race_cd_gdf.replace('N', np.nan, inplace=True)
cols_to_convert = ['White', 'Black', 'Asian', 'Hispanic']
for col in cols_to_convert:
    race_cd_gdf[col] = pd.to_numeric(race_cd_gdf[col], errors='coerce')

# Merge data to get a dataset called 'df' with the following varaibles:
# 18-29', '30-44', '18-44' '45-64', '65 and older',
# 'Women', 'In Poverty', 'Did not finish high school', 'Bachelors or more',
# 'White', 'Black', 'Asian', 'Hispanic',
# 'Voting rate'
# (Leaving out 'urbanization_pct' for now)
merge_cols = ['State name', 'Congressional district', 'CD116FP']
df = voter_turnout.merge(age_cd_gdf, on=merge_cols, how='inner') \
            .merge(sex_poverty_cd_gdf, on=merge_cols, how='inner') \
            .merge(education_cd_gdf, on=merge_cols, how='inner') \
            .merge(race_cd_gdf, on=merge_cols, how='inner')
df['18-44'] = df['18-29'] + df['30-44']
df['CD116'] = df['State name'] + ' ' + df['CD116FP'].astype(str).str.zfill(2)

# Choose Select columns
df = df[['CD116', 'Voting rate', '18-44', '45-64',
       '65 and older', 'Women', 'In Poverty', 'Did not finish high school',
       'Bachelors or more', 'White', 'Black', 'Asian', 'Hispanic']]
       # 'urbanization_pct' (not included for now)

df.loc[:, df.columns != 'Voter Data'] = df.loc[:, df.columns != 'Voter Data'].round(1)

# Export as csv
df.to_csv('./data_2018/cd_2018.csv', index=False)