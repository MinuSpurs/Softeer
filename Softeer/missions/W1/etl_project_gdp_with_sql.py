import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import sqlite3
import os
import pycountry


def log_message(msg):
    now = datetime.now().strftime('%Y-%B-%d-%H-%M-%S')  # 정해진 로그 형식에 맞춤
    if not os.path.exists("./logs"):    # 폴더가 존재하지 않으면 생성
        os.makedirs("./logs")
    with open("./logs/etl_project_log.txt", "a") as f:
        f.write(f"{now}, {msg}\n")

def extract_gdp_data():
    """
    위키피디아에서 데이터를 가져와 html로 저장
    """
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url)
    return response.text    

def transform_data(html):
    """
    html 파일을 파싱하여 원하는 데이터를 추출한 뒤 저장
    또 대륙과 국가가 매핑되어 있는 외부 csv 파일을 사용해 병합
    만약 국가명이 달라 매핑되지 않을 시, get_country_name와 get_continent_from_api 함수를 통해 대륙을 가져옴
    GDP 단위를 Million에서 Billion으로 변환
    """
    soup = BeautifulSoup(html, 'html.parser')
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
                "GDP_USD_Million": gdp_million,
                "Year": year
            })
    region_df = pd.read_csv('continents.csv')   # 지역과 국가가 매핑되어 있는 외부 csv 파일을 사용해 병합
    df = pd.DataFrame(data)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    region_df.rename(columns=lambda x: x.strip(), inplace=True)

    def get_country_name(country_name): # pycountry 라이브러리를 통해 국가명을 가져옴
        try:
            return pycountry.countries.lookup(country_name).name
        except LookupError:
            return None

    # 고유 국가 목록에 대해 한 번만 호출
    country_map_df = pd.DataFrame(df["Country"].unique(), columns=["Country"])
    country_map_df["name"] = country_map_df["Country"].apply(get_country_name)

    # 병합
    df = df.merge(country_map_df, on="Country", how="left")
    region_df["name"] = region_df["name"].astype(str).str.strip()

    # 병합 수행
    df = pd.merge(df, region_df[['Continent', 'name']], on='name', how='left')
    missing_continents = df[df['Continent'].isnull()]   # 대륙이 매핑되지 않는 국가 리스트
    if not missing_continents.empty:
        import requests
        def get_continent_from_api(country):
            try:
                response = requests.get(f"https://restcountries.com/v3.1/name/{country}")
                response.raise_for_status()
                data = response.json()
                return data[0].get("region")
            except:
                return None

        for i, row in df[df['Continent'].isnull()].iterrows():  # 대륙이 매핑되지 않는 국가를 가져와서 API를 통해 대륙을 가져옴
            continent = get_continent_from_api(row["Country"])
            if continent:
                df.at[i, "Continent"] = continent

        missing_continents = df[df['Continent'].isnull()]
        if not missing_continents.empty:
            if not os.path.exists("./logs"):
                os.makedirs("./logs")
            with open("./logs/etl_project_log.txt", "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%B-%d-%H-%M-%S')}, Countries without continent mapping:\n")
                for country in missing_continents['Country']:
                    f.write(f"- {country}\n")

    df["GDP_USD_Billion"] = (df["GDP_USD_Million"] / 1000).round(2) # 단위를 Billion으로 바꾸기 위해 1000으로 나눠준 뒤 소수점 두번째자리까지 출력
    df.drop(columns=["GDP_USD_Million"], inplace=True)  # 필요없다면, 기존 Million 단위의 GDP는 버림

    return df

def df_to_sql(df):
    conn = sqlite3.connect('World_Economies.db')

    # 원하는 컬럼만 선택해서 저장
    df_to_save = df[['Country', 'GDP_USD_Billion', 'Year', 'Continent']].copy()
    # SQL에 저장
    df_to_save.to_sql('Countries_by_GDP', conn, if_exists='replace', index=False)

    conn.close()

def load_to_json(filename="Countries_by_GDP.json"):
    conn = sqlite3.connect('World_Economies.db')
    df = pd.read_sql_query("SELECT * FROM Countries_by_GDP", conn)
    df.to_json(filename, orient="records", indent=4)    # SQL로 전체 조회 후 json 형식으로 저장
    conn.close()

def main():
    log_message("Start Extract Step")
    html = extract_gdp_data() # 데이터 추출
    log_message("End Extract Stop")

    log_message("Start Transform Step")
    df = transform_data(html)   # 원하는 데이터 형식으로 수정
    log_message("End Transform Step")

    log_message("Start SQL Save Step")
    df_to_sql(df)   # SQL 형태로 데이터 변환
    log_message("End SQL Save Step")

    log_message("Start Load Step")
    load_to_json()  # json 형식으로 저장
    log_message("End Load Step")

    log_message("Start SQL Query for Analysis")
    conn = sqlite3.connect('World_Economies.db')
    cursor = conn.cursor()

    print("\n[GDP ≥ 100B USD Countries]")   # 100B USD보다 GDP가 높은 나라만 출력
    cursor.execute("""
        SELECT Country, GDP_USD_Billion
        FROM Countries_by_GDP
        WHERE GDP_USD_Billion >= 100 
        ORDER BY GDP_USD_Billion DESC;
    """)    # GDP가 100B보다 높은 나라를 내림차순으로 출력
    for row in cursor.fetchall():
        print(row)

    print("\n[Top 5 GDP Average per Continent]")
    cursor.execute("""  
        SELECT Continent, ROUND(AVG(GDP_USD_Billion), 2) AS avg_gdp
        FROM (
            SELECT Continent, GDP_USD_Billion,
                   ROW_NUMBER() OVER (PARTITION BY Continent ORDER BY GDP_USD_Billion DESC) as rn
            FROM Countries_by_GDP
            WHERE Continent IS NOT NULL
        )
        WHERE rn <= 5
        GROUP BY Continent;
    """)    # SQLite에서는 TOP 을 지원하지 않기 때문에 ROW_NUMVER를 통하여 각 지역에 번호를 매겨서 사용
    for row in cursor.fetchall():
        print(row)

    conn.close()
    log_message("End SQL Query for Analysis")

if __name__ == "__main__":
    main()