import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import os


def log_message(msg):
    now = datetime.now().strftime('%Y-%B-%d-%H-%M-%S')
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    with open("./logs/etl_project_log.txt", "a") as f:
        f.write(f"{now}, {msg}\n")

def extract_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    rows = table.find_all('tr')

    data = []
    for row in rows[1:]:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 3:
            country = cols[0].get_text(strip=True)
            gdp_million = cols[1].get_text(strip=True).replace(",", "")
            year = cols[2].get_text(strip=True)

            try:
                gdp_million = int(gdp_million)
            except:
                continue

            data.append({
                "Country": country,
                "GDP_Million_USD": gdp_million,
                "Year": year
            })

    return pd.DataFrame(data)

def transform_data(df):
    df["GDP_Billion_USD"] = (df["GDP_Million_USD"] / 1000).round(2)
    df.drop(columns=["GDP_Million_USD"], inplace=True)
    return df

def load_to_json(df, filename="Countries_by_GDP.json"):
    df.to_json(filename, orient="records", indent=4)

def main():
    log_message("Start Extract Step")
    df = extract_gdp_data()
    log_message("End Extract Stop")
    log_message("Start Transform Step")
    df = transform_data(df)
    log_message("End Transform Step")
    log_message("Start Load Step")
    load_to_json(df)
    log_message("End Load Step")

if __name__ == "__main__":
    main()