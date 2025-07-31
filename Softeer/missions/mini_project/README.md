# Mini project

---

Team #2 : DE박건희, DE임채현, DE오민우

프로토타입 : [축구 선수 분석](http://3.35.135.180/)  

---

# 목차

[I. 개요](#I-개요)

[II. 해결 방안](#II-해결-방안)

[III. 방법론](#III-방법론)

[IV. 프로토타입](#IV-프로토타입)

[V. 결과 분석](#V-결과-분석)

[VI. 결론 및 한계점](#VI-결론-및-한계점)

---

# I. 개요

- 외국인 선수를 영입할 때, ‘누굴 먼저 살펴볼지’, ‘정말 우리 팀 전술에 맞는지’, ‘시장 가치 대비 가성비가 좋은지’에 대한 판단 기준이 없다.
- [WhoScored](https://1xbet.whoscored.com/), [Fotmob](https://www.fotmob.com/) 같은 통계가 존재하지만, 정보 확인을 위해선 선수 하나하나 들어가 봐야하며, 전술 조건에 따라 선수를 필터링하는 기능도 없다.
- 이로 인해, 디렉터는 에이전트들의 추천이나 제한된 영상만으로 결정을 내려야 하며, 이로 인해 연봉과 이적료가 낭비되는 영입 실패가 반복된다.
- 또한 스카우터들이 정해진 타겟 없이 선수를 스카우팅하기 위해 타지로 떠나 팀의 비용적인 측면에서도 큰 손실이 항상 이어진다.
- 높은 퍼포먼스를 예상한 이 과정을 통해 영입된 억대의 연봉을 받는 용병이 실제로 원하는 만큼의 퍼포먼스를 보이지 못하면 이적료와 연봉 손실 뿐 아니라 팀 성적 하락으로 인한 중계권료, 관중 수입 감소로 인해 수십억원의 손실이 발생할 수 있다.
- 이러한 문제를 해결하기 위하여, 우리는 선수 통계 사이트를 통해 선수들의 수많은 스탯들을 모으고, 이를 직관적으로 볼 수 있게 해주며, 팀 내 선수와 비교를 통해 확실한 의사결정에 도움이 될 수 있도록 도와주는 웹 사이트를 개발했다.
- 이는 기존에 자본이 부족하여 제대로된 영입 리스트조차 제작할 수 없고 데이터 측면으로 선수 영입을 하기 힘든 K리그 팀들에게 큰 도움이 될 것으로 기대한다.

---

# II. 해결 방안

- 데이터의 격차를 이용하여 저비용으로 영입한 선수가 맹활약하여 팀을 상위 리그로 승격시킬 경우, 그 가치는 수백 억에서 최대 2,500억원(EPL 기준)에 달하는 천문학적인 수익으로 이어진다진다. 추가로 선수의 몸값도 크게 상승하여 높은 이적료 수익을 기대할 수 있다. 이는 결과적으로 구단의 가치 상승 효과를 기대할 수 있다.다.
- 전 세계 선수들의 경기력 통계와 시장 가치 정보를 통합하여 선수 퍼포먼스 데이터를 구축한다. 이 데이터셋을 바탕으로 시장 가치 대비 퍼포먼스 효율, 즉 가성비가 높은 선수를 우선 필터링하며, 구단은 여기에 필요 포지션, 예산, 선호하는 선수 스타일 조건을 입력해 조건에 부합하는 선수 리스트를 자동 추천받는다. 이를 통해 영입 대상자 리스트를 빠르게 압축하고 데이터 기반으로 검증하여 의사결정 속도와 정확도를 모두 높인다.
- 리그 별 수준의 차이를 고려하기 위한 리그 가중치를 도입하여 스탯을 일관성있게 보정해주는 방식으로 하위 리그와 상위 리그 간의 수준 차이까지 고려한 객관적인 지표를 제공한다.
- 먼저 데이터 해석의 문제를 해결하려한다. K리그 20골과 잉글랜드 프리미어리그 15골의 가치는 분명 다르다. 국제 축구 역사 통계 연맹(IFFHSL)에서 제공하는 리그 수준별 편차를 적용하여 어떤 리그의 선수든 K리그 기준으로 스탯을 자동 보정한다. 그 결과는 동일선상에서 최대한 객관적으로 비교할 수 있는 표준화된 퍼포먼스 점수를 제공한다.
- 결론적으로 이 솔루션은 독자적인 표준화 및 예측 모델을 갖춘 의사결정 보조 시스템으로서 기술적, 시기적, 가격적 우위를 통해 기존에 없던 새로운 시장을 만들어 나갈 수 있을 것으로 기대한다.

<aside>
💡

## 비즈니스 아이디어

- 주제 : 저예산 축구팀을 위한 '머니볼' 스카우팅 플랫폼
- 데이터 : [WhoScored](https://1xbet.whoscored.com/), [Fotmob](https://www.fotmob.com/) 플랫폼의 데이터를 기반으로 선수들의 통계를 수집하여 가공
- 판매 희망자 : 전문 데이터 분석가 없이 선수 영입과 스카우팅을 병행해야 하는 소규모 하위 리그 구단의 의사결정권자(디렉터)
- 판매 희망가 : 월 1,000만원 이상
    - k2 League 기준 선수의 평균 연봉인 약 1억 3천만원보다 적은 금액
    - 시스템을 통해 선수 영입하여 승격에 성공한다면, 10배 이상의 리턴으로 다가올 수 있다.
</aside>

---

# III. 방법론

1. ETL 파이프라인
    1. Extract
        
        ```python
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import pandas as pd
        import time
        import undetected_chromedriver as uc
        import os  # 파일 저장을 위해 os 모듈 추가
        
        def scrape_player_per90_html(url, output_dir="per90_html_files"):
            """
            선수단 페이지에서 코치와 골키퍼를 제외한 선수들의 프로필 페이지를 방문하여
            '90분당' 통계로 전환한 후, 해당 페이지의 HTML 소스를 파일로 저장합니다.
        
            인자:
                url (str): 고이아스 선수단 페이지의 URL.
                output_dir (str): HTML 파일을 저장할 디렉토리 경로.
            """
            options = uc.ChromeOptions()
            # options.add_argument('--headless') # 백그라운드 실행. 디버깅 시에는 주석 처리
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        
            # 출력 디렉토리 생성
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"출력 디렉토리 '{output_dir}'를 생성했습니다.")
        
            driver = uc.Chrome(options=options)
            print("undetected_chromedriver를 사용하여 브라우저를 시작했습니다.")
        
            try:
                driver.get(url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.css-e3ea0x-SquadTable tbody tr"))
                )
                print("메인 선수단 페이지가 성공적으로 로드되었습니다.")
        
                # 모든 선수 로드를 위해 페이지를 끝까지 스크롤합니다.
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                print("모든 선수 로드를 위해 페이지를 끝까지 스크롤했습니다.")
        
                squad_table_body = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.css-e3ea0x-SquadTable tbody"))
                )
                player_rows_elements = squad_table_body.find_elements(By.TAG_NAME, "tr")
        
                player_links_info = []
                for row_index, row in enumerate(player_rows_elements):
                    try:
                        position_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                        player_position = position_element.text.strip()
        
                        if player_position == "Coach" or player_position == "GK":
                            print(f"선수단: {row_index + 1}번째 행의 {player_position}은(는) 건너뜜.")
                            continue
        
                        player_name_element = row.find_element(By.CSS_SELECTOR, "span.css-1v1x2yd-SquadPlayerName")
                        player_name = player_name_element.text.strip()
                        player_url_element = row.find_element(By.CSS_SELECTOR, "a.css-19p22et-SquadPlayerLink")
                        player_page_url = player_url_element.get_attribute('href')
        
                        player_links_info.append({"name": player_name, "position": player_position, "url": player_page_url})
        
                    except Exception as e:
                        print(f"선수단: {row_index + 1}번째 행에서 선수 정보 추출 실패: {e}")
                        continue
        
                for player_info in player_links_info:
                    player_name = player_info['name']
                    player_position = player_info['position']
                    player_page_url = player_info['url']
        
                    print(f"\n--- 선수: {player_name} (포지션: {player_position}) 처리 중 ---")
        
                    try:
                        driver.get(player_page_url)
                        print(f"-> 선수 페이지로 이동: {player_page_url}")
        
                        # 'DetailedStatsCSS' 컨테이너가 나타날 때까지 기다립니다.
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "css-1i210f4-DetailedStatsCSS"))
                        )
                        print(f"-> {player_name}의 'DetailedStatsCSS' 컨테이너 로드 완료.")
        
                        # 통계 필터 버튼이 클릭 가능해질 때까지 명시적으로 기다립니다.
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.css-12ltoon-FilterButtonsContainer button"))
                            )
                            print(f"-> {player_name}의 통계 필터 버튼이 클릭 가능합니다.")
                        except Exception as e:
                            print(f"-> 경고: {player_name}의 통계 필터 버튼을 찾거나 클릭할 수 없는 상태입니다: {e}")
                            print("-> 통계 데이터가 없을 수 있으므로 HTML 저장 없이 다음 선수로 이동합니다.")
                            continue  # 버튼 없으면 통계 없는 것으로 판단하고 다음 선수로 넘어감
        
                        # '90분당' 버튼 클릭 시도
                        try:
                            total_button_activated = False
                            try:
                                active_total_button = driver.find_element(By.XPATH,
                                                                          "//button[contains(@class, 'css-1rxiuro-FilterButton') and (text()='합계' or text()='Total')]")
                                total_button_activated = True
                            except:
                                pass  # '합계' 버튼이 활성화되어 있지 않음
        
                            if total_button_activated:  # '합계'가 활성화되어 있다면 '90분당' 버튼을 클릭해야 함
                                per_90_button = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-1giracq-FilterButton"))
                                )
        
                                driver.execute_script("arguments[0].click();", per_90_button)
                                print(f"-> '{player_name}' 페이지에서 '90분당' 버튼을 클릭했습니다.")
        
                                # 데이터 업데이트를 위한 충분한 대기
                                time.sleep(3)  # 클릭 후 통계 업데이트를 위한 짧은 대기
        
                                # '90분당' 통계가 실제로 업데이트되었는지 확인하는 명시적 대기
                                # '득점' 통계 값이 DOM에 나타날 때까지 기다림 (값 자체의 변화보다는 요소의 안정화)
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH,
                                                                    "//div[contains(@class, 'DetailedStatsCSS')]//div[contains(@class, 'StatTitle') and text()='득점']/following-sibling::div[contains(@class, 'StatCSS')]//span"))
                                )
                                print(f"-> '{player_name}'의 '90분당' 통계 데이터 업데이트 확인 완료.")
        
                            else:  # '합계' 버튼이 활성화되어 있지 않다면, '90분당'이 이미 활성화되어 있거나 통계 자체가 없음
                                print(f"-> '90분당' 버튼이 이미 활성화되어 있거나 클릭할 필요가 없습니다. (현재 비활성화된 버튼: '합계')")
        
                        except Exception as e:
                            print(f"-> 경고: '{player_name}' 페이지에서 '90분당' 버튼 처리 중 오류 발생 (클릭 실패): {e}")
                            print("-> HTML 파일이 '합계' 통계 상태로 저장될 수 있습니다.")
                            # 오류 발생 시에도 HTML 저장은 시도합니다.
        
                        # '90분당'으로 전환된 후의 페이지 HTML 소스 저장
                        sanitized_player_name = "".join(c for c in player_name if c.isalnum() or c in [' ', '_']).strip()
                        filename = os.path.join(output_dir, f"{sanitized_player_name}_per90.html")
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        print(f"-> '{player_name}'의 '90분당' HTML 소스를 '{filename}'에 저장했습니다.")
        
                    except Exception as e:
                        print(f"오류: {player_name}의 페이지 처리 중 예상치 못한 오류가 발생했습니다: {e}")
                        # 이 단계에서는 HTML 저장을 하지 않습니다. (위에서 버튼 클릭 성공 시에만 저장)
        
                    finally:
                        # 다음 선수 처리를 위해 메인 선수 목록 페이지로 직접 이동
                        driver.get(url)
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "table.css-e3ea0x-SquadTable tbody tr"))
                        )
                        print("메인 선수단 페이지로 돌아갔습니다.")
        
            except Exception as e:
                print(f"전체 스크래핑 과정 중 예상치 못한 오류가 발생했습니다: {e}")
            finally:
                driver.quit()
        
        # 선수단 페이지의 URL
        squad_url = "https://www.fotmob.com/teams/8355/squad/"
        
        # 스크래퍼 실행 (HTML 파일 저장)
        scrape_player_per90_html(squad_url)
        
        print("\n--- 모든 선수별 '90분당' 통계 HTML 파일 저장이 완료되었습니다. ---")
        ```
        
        - 선수들의 스탯이 경기별로 저장되어 있는 FOTMOB 사이트에서 데이터를 가져왔다.
        - 자동화 브라우저 실행: 파이썬의 `Selenium` 라이브러리와 `undetected-chromedriver`를 활용하여 봇 탐지를 우회하고 실제 사용자와 유사한 환경에서 데이터에 접근했다. 이를 통해 동적으로 로딩되는 웹페이지의 정보를 안정적으로 수집할 수 있었다.
        - 선수 목록 확보 및 필터링: 특정 팀의 선수단 페이지에 접속하여 골키퍼(GK)와 코치를 제외한 모든 필드 플레이어의 이름과 개인 통계 페이지 URL을 추출했다. → 골키퍼 포지션 경우에는 프로토타입에서는 제외했지만, 추후 추가 예정이다.
        - '90분당' 데이터 정규화: 각 선수의 개인 페이지로 이동한 후, 모든 통계를 '90분당(Per 90 minutes)' 기준으로 변환하는 작업을 자동화했다. 이는 선수별 출전 시간의 차이를 보정하고 모든 선수를 동일한 조건에서 비교하기 위한 핵심적인 전처리 과정이다.
        - HTML 저장: '90분당' 통계로 전환된 페이지의 전체 HTML 소스를 선수별 파일로 로컬 환경에 저장했다.
        - 이 코드를 통해 특정 팀의 선수단의 90분당 통계 HTML을 모두 가져올 수 있다.
    2. Transform & Load
        
        ```python
        import os
        import json
        import pandas as pd
        import numpy as np
        from bs4 import BeautifulSoup
        from sklearn.preprocessing import MinMaxScaler
        
        def parse_meta_description(content):
            data = {}
            parts = content.split(',', 1)
            if len(parts) == 2:
                data['이름'] = parts[0].strip()
                rest = parts[1]
                items = [item.strip() for item in rest.split(',')]
                for item in items:
                    if ':' in item:
                        k, v = item.split(':', 1)
                        data[k.strip()] = v.strip()
            else:
                data['이름'] = content.strip()
            return data
        
        def extract_from_html_file(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
        
            data_dict = {}
            
            json_ld_tags = soup.find_all('script', type='application/ld+json')
            for tag in json_ld_tags:
                try:
                    json_data = json.loads(tag.string)
                    if isinstance(json_data, dict) and json_data.get('@type') == 'BreadcrumbList':
                        items = json_data.get('itemListElement', [])
                        for item in items:
                            if isinstance(item, dict) and item.get('position') == 2:
                                data_dict['리그'] = item.get('name')
                                break
                except:
                    continue
        
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.has_attr('content'):
                data_dict.update(parse_meta_description(meta_desc['content']))
        
            position_div = soup.find('div', class_='css-1g41csj-PositionsCSS')
            if position_div:
                data_dict['포지션'] = position_div.get_text(strip=True)
        
            stat_items = soup.find_all('div', class_='css-1v73fp6-StatItemCSS')
            for item in stat_items:
                title_div = item.find('div', class_='css-2duihq-StatTitle')
                value_div = item.find('div', class_='css-1mb10ua-StatValue')
                if title_div and value_div:
                    key = title_div.get_text(strip=True)
                    value_span = value_div.find('span')
                    value = value_span.get_text(strip=True) if value_span else ''
                    data_dict[key] = value
        
            stat_boxes = soup.find_all('div', class_='css-vohuhg-StatBox')
            for box in stat_boxes:
                value_div = box.find('div', class_='css-170fd60-StatValue')
                title = box.find('span', class_='css-1xy07gm-StatTitle')
                if value_div and title:
                    data_dict[title.text.strip()] = value_div.get_text(strip=True)
        
            rating_div = soup.find('div', class_='css-ibpnnl-PlayerRatingCSS')
            if rating_div:
                rating_value = rating_div.find('span')
                if rating_value:
                    data_dict['평점'] = rating_value.text.strip()
        
            return data_dict
        
        def extract_multiple_html_to_csv(html_dir, csv_path):
            rename_map = {
                "기회 창출": "찬스 메이킹",
                "볼 뺏김": "볼 뺏긴 수",
                "공격 지역 점유율": "전방 압박 성공",
                "막힘": "막힌 슛",
                "드리블로 제침": "드리블 성공 횟수",
                "드리블 성공": "드리블 성공 비율",
                "획득한 파울": "파울 획득",
                "페널티킥 받음": "페널티킥 얻음",
                "회복": "리커버리"
            }
        
            data_list = []
            for filename in os.listdir(html_dir):
                if filename.endswith(".html"):
                    filepath = os.path.join(html_dir, filename)
                    player_data = extract_from_html_file(filepath)
                    data_list.append(player_data)
        
            df = pd.DataFrame(data_list).rename(columns=rename_map)
        
            front_cols = ['이름', '팀', '나이', '국가', '키', '셔츠', '주로 사용하는 발', '포지션', '선발', '경기', '출전 시간', '시장 가치', '경고', '퇴장', '평점', '득점']
            df = df[[col for col in front_cols if col in df.columns] + [col for col in df.columns if col not in front_cols]]
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"HTML → CSV 저장 완료: {csv_path}")
        
        def normalize_percentage_column(series):
            def convert(val):
                if pd.isna(val): return 0.0
                if isinstance(val, str) and "%" in val:
                    val = val.replace("%", "")
                try:
                    return float(val) / 100
                except:
                    return 0.0
            return series.apply(convert)
        
        def calculate_scores(numeric_stats_df):
            scaler = MinMaxScaler()
            normalized = pd.DataFrame(scaler.fit_transform(numeric_stats_df.fillna(0)), columns=numeric_stats_df.columns, index=numeric_stats_df.index)
        
            scores = pd.DataFrame(index=numeric_stats_df.index)
        
            def safe_mean(df, cols):
                existing_cols = [col for col in cols if col in df.columns]
                if not existing_cols:
                    return pd.Series(np.nan, index=df.index)
                return df[existing_cols].mean(axis=1)
        
            scores['공격력'] = safe_mean(normalized, ['득점', '예상 골 (xG)', 'xG 유효 슈팅 (xGOT)', '유효 슈팅', '슛', '상대편 박스 내에서의 터치'])
            scores['창의성'] = safe_mean(normalized, ['어시스트', '예상 어시스트 (xA)', '찬스 메이킹', '패스', '크로스', '드리블', '롱패스'])
            scores['전진 기여도'] = safe_mean(normalized, ['드리블', '정확한 긴 패스', '전방 압박 성공'])
            scores['패스 능력'] = safe_mean(normalized, ['성공한 패스', '패스 정확도', '찬스 메이킹'])
            scores['수비력'] = safe_mean(normalized, ['태클', '가로채기', '리커버리'])
            scores['경합력'] = safe_mean(normalized, ['볼 경합', '공중 경합'])
            scores['활동량'] = safe_mean(normalized, ['리커버리', '전방 압박 성공', '파울 획득', '터치'])
        
            stability_cols = ['반칙', '경고', '퇴장', '볼 뺏긴 수']
            for col in stability_cols:
                if col not in normalized.columns:
                    normalized[col] = 0
            scores['안정성'] = 1 - normalized[stability_cols].mean(axis=1)
        
            return scores
        
        def process_player_stats(input_csv_path, output_csv_path):
            df = pd.read_csv(input_csv_path)
            df = df[df['리그'].isin(['Serie B 2025', 'K-League 1 2025', 'Premier League 2024/2025', 'Bundesliga 2024/2025', 'LaLiga 2024/2025'])]
            df['시장 가치'] = df['시장 가치'].fillna('€0')
            df[['셔츠', '선발', '경기']] = df[['셔츠', '선발', '경기']].astype('Int64')
        
            df['드리블'] = df['드리블 성공 횟수'] * normalize_percentage_column(df['드리블 성공 비율'])
            df['패스'] = df['성공한 패스'] * normalize_percentage_column(df['패스 정확도'])
            df['크로스'] = df['성공한 크로스'] * normalize_percentage_column(df['크로스 정확도'])
            df['태클'] = df['태클 성공'] * normalize_percentage_column(df['태클 성공 %'])
            df['볼 경합'] = df['볼 경합 성공'] * normalize_percentage_column(df['볼 경합 성공 %'])
            df['공중 경합'] = df['공중 볼 경합 성공'] * normalize_percentage_column(df['공중 볼 경합 성공 %'])
            df['롱패스'] = df['정확한 긴 패스'] * normalize_percentage_column(df['롱 패스 정확도'])
        
            info_cols = ['이름', '포지션', '팀', '나이', '국가', '주로 사용하는 발', '키', '셔츠', '선발', '경기', '출전 시간', '시장 가치', '리그', '평점']
            stats_cols = [col for col in df.columns if col not in info_cols]
        
            df[stats_cols] = df[stats_cols].apply(pd.to_numeric, errors='coerce')
        
            if '리그' in df.columns:
                league_weights = {
                    'K-League 1 2025': 0.7,
                    'Serie B 2025': 0.55,
                    'Paulista A1 2025': 0.4
                }
                weights = df['리그'].map(league_weights).fillna(1.0)
                df[stats_cols] = df[stats_cols].multiply(weights, axis=0)
        
            score_df = calculate_scores(df[stats_cols])
            cols_to_normalize = stats_cols + list(score_df.columns)
            final_df = pd.concat([df[info_cols], df[stats_cols], score_df], axis=1)
            numeric_part = final_df[cols_to_normalize].fillna(0)
            
            scaler = MinMaxScaler()
            normalized_data = scaler.fit_transform(numeric_part)
            
            normalized_df = pd.DataFrame(normalized_data, columns=cols_to_normalize)
            normalized_df = normalized_df.applymap(lambda x: int(round(x * 100)))
            final_output_df = pd.concat([final_df[info_cols].reset_index(drop=True), normalized_df.reset_index(drop=True)], axis=1)
            final_output_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
            print(f"최종 정규화 CSV 저장 완료: {output_csv_path}")
        
        if __name__ == "__main__":
            html_dir = "per90_stats"
            intermediate_csv = "test.csv"
            final_output_csv = "종합지표_선수능력치_정규화.csv"
        
            extract_multiple_html_to_csv(html_dir, intermediate_csv)
            process_player_stats(intermediate_csv, final_output_csv)
        
            if os.path.exists(intermediate_csv):
                os.remove(intermediate_csv)
                print(f"{intermediate_csv} 파일이 삭제되었습니다.")
            else:
                print(f"{intermediate_csv} 파일이 존재하지 않습니다.")
        ```
        
        - 수집된 원시 HTML 데이터는 분석에 바로 사용하기 어렵기 때문에, 다음과 같은 Transform, Load 파이프라인을 구축하여 최종 분석용 데이터셋을 생성했다 :
        - 데이터 파싱: 파이썬의 `BeautifulSoup` 라이브러리를 사용하여 저장된 HTML 파일들로부터 이름, 나이, 포지션과 같은 기본 정보와 '득점', '패스 성공률' 등 수십 개의 상세 스탯을 파싱(Parsing)하여 구조화된 데이터프레임 형태로 변환했다.
        - 데이터 변환 및 보정 (Transformation): 추출된 데이터를 분석 목적에 맞게 가공하고 가치를 더하는 과정을 거쳤습니다.
            - 파생 스탯 생성: '드리블 성공 횟수'와 '드리블 성공률'을 조합하여 '90분당 유효 드리블'과 같은 새로운 종합 지표를 생성하여 단편적인 스탯만으로는 알 수 없는 선수의 실제 영향력을 측정했다.
            - 리그 수준 보정: 본 플랫폼의 핵심 기술로, IFFHS(국제축구역사통계연맹)의 리그 랭킹을 참고하여 리그별 가중치를 설정했다. 이후 모든 선수의 스탯에 이 가중치를 적용하여, 다른 리그에서 뛰는 선수들을 K리그 기준으로 객관적으로 비교할 수 있는 표준화된 스탯을 산출했다.
            - 종합 능력치 산출: 표준화된 세부 스탯들을 바탕으로 '공격력', '창의성', '수비력', '안정성' 등 직관적으로 이해할 수 있는 종합 능력치 점수를 계산했다.
        - 최종 정규화 및 저장 (Loading): 최종적으로 모든 스탯과 종합 능력치를 `MinMaxScaler`를 사용하여 0점에서 100점 사이의 점수로 정규화(Normalization)했습니다. 이를 통해 어떤 선수든 리그 수준까지 보정하여 직관적으로 기량을 비교하고 평가할 수 있는 최종 데이터셋을 완성하고 CSV 파일로 저장했다.

1. 웹페이지 및 지표 개발
- 본 프로젝트는 단순히 CSV 파일로만 선수들의 정보를 저장하는 것에 그치지 않고, 웹 페이지의 여러 인터페이스를 통해 직접적인 선수 비교에 도움이 될만한 UI 툴을 개발했다.
- 또한 단순 경기 통계로는 해석하기 어려운 스탯들을 조합하여 직관적으로 보일 수 있는 스탯들 만들어, 디렉터들이 기존 선수와 영입 예상 선수를 비교하기 편하게 제공한다.
- [축구 선수 분석](http://3.35.135.180/) 플랫폼에서는 객관적으로 비교하길 원하는 구단의 선수 데이터를 업로드하고, 필터를 적용하는 것으로 사용자가 희망하는 능력을 가진 선수의 데이터를 열람할 수 있다.
- 필터링된 선수 데이터는 ‘시장가치’, ‘평점’, ‘득점’, ‘어시스트’, ‘나이’에 따라 오름차순과 내림차순으로 선택하여 정렬할 수 있으며, 자세한 열람을 희망하는 선수가 있다면, 해당 선수를 클릭하여 상세 페이지에서 선수에 대한 상세 스탯을 열람할 수 있다. 추가적으로 필요 시에 다른 구단의 선수와의 비교도 가능하다.
- 선수 비교 페이지에서 비교하길 희망하는 선수를 리스트 박스에서 선택하면 해당 선수에 대한 상세 스탯이 함께 출력되며, 각 스탯 별로 두 선수의 스탯을 세부적으로 비교할 수 있다.
- 선수들의 종합적인 능력치를 바탕으로 수식을 통해 8개의 환산 능력치를 산출하고, 해당 스탯을 기준으로 팔각형의 그래프 형태로 능력치를 시각화하여 쉽게 볼 수 있다.

---

# IV. 프로토타입

- 시나리오
    - 현재 FC안양 디렉터는 리영직 선수(중앙 미드필더)의 나이로 인한 폼 하락을 대비하여 비슷한 스타일과 비슷한 수준의 선수를 데려오려 한다.
    - 하지만 리영직 선수를 판매할 때, 나이가 많아 많은 돈을 회수하기에는 힘들다.
    - 그래서 리영직 선수의 시장 가치보다 더 싼 선수를 영입하려 한다.
    - 리영직 선수의 스타일은 중앙에서 많은 활동량으로 수비에 치중하며, 리그 내의 동포지션 선수들보다 많은 터치와 패스로 공격 전개를 이끌어주는 공격의 시발점 역할을 해주는 선수다.
    - 볼 경합 상황에서의 모습은 아쉽지만, 공을 뺏겨도 바로 탈환하는 능력(리커버리)는 좋은 선수다.
    - 이런 선수를 대체하기 위해서 우리는 축구 선수 데이터 분석 프로토타입을 이용하여 선수를 찾아보려 한다.
        <img width="1285" height="683" alt="스크린샷_2025-07-31_오후_5 06 09" src="https://github.com/user-attachments/assets/d20dcf6f-d2b1-4f7d-8899-8d92a6e9751d" />

        
    - 프로토타입이기 때문에 먼저 수집한 선수들의 csv를 페이지에 업로드 해준다.
    - 추후에는 내부에서 csv를 자동으로 읽어오는 기능을 추가할 예정이다.
        <img width="1301" height="709" alt="스크린샷_2025-07-31_오후_5 06 42" src="https://github.com/user-attachments/assets/54898b16-f1d7-4a41-bca5-b63dffaf7173" />

        
    - csv 업로드 후에 [필터 조건 설정] 버튼을 클릭하여 원하는 선수의 조건을 선택해준다.
        <img width="1285" height="811" alt="스크린샷_2025-07-31_오후_5 30 13" src="https://github.com/user-attachments/assets/5aaea04a-0080-466e-887d-480f13e3445e" />

        <img width="1295" height="540" alt="스크린샷_2025-07-31_오후_5 28 15" src="https://github.com/user-attachments/assets/d3c1c7a0-509b-4b22-bb36-6dd38aadc1f6" />

        
    - 원하는 선수의 조건을 입력해준다.
    - 이때 점수의 범위를 정해줄 수 있다.
        <img width="1264" height="463" alt="스크린샷_2025-07-31_오후_5 28 28" src="https://github.com/user-attachments/assets/d725f500-bb0a-4a5c-9333-010e1235d77f" />
        
        
    - 필터링 조건 선택을 하면 조건에 맞는 선수들이 리스트업이 된다.
    - 이때 정렬 기준을 여러개로 오름차순/내림차순으로 정렬할 수 있다.
        <img width="962" height="956" alt="스크린샷_2025-07-31_오후_5 08 38" src="https://github.com/user-attachments/assets/4ddb5bf6-438d-4ce0-80fd-aefdaae9453f" />

        
    - 이때 조건에 맞는 것 같은 선수를 발견한 뒤 클릭하게 되면 선수의 전체적인 스탯을 볼 수 있다.
    - 리영직 선수와 비교를 위해 [비교하기] 버튼을 클릭해본다.
        <img width="1028" height="893" alt="스크린샷_2025-07-31_오후_5 09 30" src="https://github.com/user-attachments/assets/ea36f62a-fb76-46c1-9e9a-b45ad3109085" />

        
    - 비교할 선수를 정해준 뒤 [비교 시작]을 누르게 되면, 상단에 상세 스탯 비교가 나오게 된다.
    - 이때 바 그래프를 통해 누가 어떤 스탯이 더 높은지 직관적으로 확인할 수 있다.
        <img width="882" height="876" alt="스크린샷_2025-07-31_오후_5 12 16" src="https://github.com/user-attachments/assets/e9fc1e9e-0230-4a8c-8676-413a4122b758" />

        
    - 스크롤을 내려보면 종합 능력치 비교가 나오게 되는데, 상세 스탯을 조합하여 만든 8개의 스탯을 레이저 형태로 직관적으로 볼 수 있게 해준다.
    - 이를 통해 조금 더 조사하여 스카우트를 보낼 만 한지, 그럴 정도는 아닌지 의사 결정에 보조할 수 있으며, 이 선수를 소개할 때 보조 도구로 사용할 수 있을 것으로 기대한다.

---

# V. 결과 분석

- 위 시나리오 분석 결과, Giovanni Pavani라는 브라질 2부리그의 선수는 리영직 선수보다 낮은 시장가치에 비슷한 플레이 스타일을 가지고 있는 것으로 기대할 수 있다.
- 이는 리그 보정 계수를 통해 K리그에 비해 브라질 2부리그에 더 낮은 가중치를 줬을 때의 결과이다.
- 그럼에도 불구하고, 비슷한 스탯을 보이는 것으로 확인이 되며, 나이 또한 전성기로 접어드는 나이기 때문에 Giovanni Pavani의 에이전트를 통해 연봉을 문의하거나 경기를 보러 스카우트를 보내봐도 좋겠다는 판단이 설 수 있다.
- 또한 상세 스탯 비교를 해봤을 때, 리영직 선수보다 득점 측면에서 조금이지만 더 나은 성능을 보여주는 것을 확인하여, 선수에게 리영직 선수 대비 조금은 더 공격적으로 움직일 수 있도록 할 수 있을 것으로 기대하며, 볼 경합에서도 앞서는 모습을 봤을 때, 중원에서 더 강한 싸움을 붙힐 수 있을 것 같다.

---

# VI. 결론 및 한계점

- 본 프로젝트는 아직까지 데이터 기반의 선수 영입에 어려움을 겪고 있는 구단에게 실질적인 해결책을 제시한다. 이 플랫폼은 예산과 정보가 부족한 K리그 구단의 디렉터들이 '감'과 '인맥'에 의존하던 기존의 영입 방식에서 벗어나, 데이터에 근거하여 실패 확률을 최소화하고 성공 가능성을 높이는 강력한 보조 장치로서 작동할 수 있다. 이를 통해 불필요한 스카우트 비용 및 분석팀 운영 비용을 절감하고, 구단 재정의 안정성을 높이는 효과를 기대할 수 있다.
- 본 플랫폼의 진정한 가치는 인간 전문가의 역할을 대체하는 것이 아니라, 그들의 의사결정을 강화하고 시간을 절약시키는 데 있다. 전 세계 수십만 명의 선수 중 1차적으로 주목해야 할 '저평가된 원석' 후보군을 단시간에 추려냄으로써, 스카우터와 디렉터는 단순 반복적인 필터링 업무에서 벗어나 심층적인 영상 분석, 인성 면담, 전술 적합성 검토 등 더 높은 가치를 창출하는 질적 분석에 집중할 수 있다.
- 그러나 다음과 같은 한계점도 존재한다:
    - 측정 불가능한 피지컬 데이터: '속도'나 '활동량'과 같이 영상이나 직관으로만 체감할 수 있는 선수의 순수 피지컬 능력은 데이터만으로 판단하기 어렵다.
    - 정성적 요소의 부재: 선수의 리더십, 성실성, 팀 융화 능력과 같은 인성적 측면이나 새로운 환경에 대한 문화적 적응력은 통계로 측정할 수 없는 영역이다.
    - 데이터의 한계: 공개된 데이터 소스에 의존하므로 데이터의 완전한 신뢰성을 담보하기 어렵고, 히트맵이나 오프더볼 움직임 같은 깊이 있는 전술 데이터는 제공하지 못한다. 이는 구단 자체별로 데이터팀을 운영해야하는 이유가 될 수 있다.
    - 통계의 맥락 부족: 데이터는 선수가 '무엇을 했는지'는 보여주지만, '왜 그런 플레이를 했는지'와 같은 맥락적 정보는 담지 못한다. 예를 들어, 낮은 패스 성공률이 선수의 능력 부족이 아닌, 위험을 감수하는 플레이 스타일 때문일 수 있다.

---
