"""
Bryan Ma
DS4200
Created to merge final project csvs into one dataframe
"""
import pandas as pd

# REPLACE PATHS WITH YOUR LOCAL DATA PATH
mental_illnesses_csv_path = "DS4200_Final_data/1- mental-illnesses-prevalence.csv"
country_GDP_path = "DS4200_Final_data/List_of_countries_by_GDP_(nominal)_1.csv"


def get_data():
    # read in respective csvs
    mental_illness = pd.read_csv(mental_illnesses_csv_path)
    gdp = pd.read_csv(country_GDP_path)

    # format csvs for readability and remove unwanted columns
    mental_illness.drop(columns=["Code"], inplace=True)
    gdp.drop(columns=["World Bank\n(2024)", "United Nations\n(2024)"], inplace=True)

    mental_illness_new_column_names = ["Country", "Year", "Schizophrenia", "Depressive Disorders", "Anxiety Disorders",
                                       "Bipolar Disorders", "Eating Disorders"]
    mental_illness.columns = mental_illness_new_column_names

    gdp_new_column_names = ["Country", "Country GDP (millions USD)"]
    gdp.columns = gdp_new_column_names

    data = mental_illness.merge(gdp, on="Country")

    data.to_csv("ds4200_final_data.csv", index=False)

get_data()

