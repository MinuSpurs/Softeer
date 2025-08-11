import time
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

def clean_text(text):
    text = re.sub(r'[^\w\sㄱ-ㅎ가-힣.,!?]', '', text)  # 이모지 및 특수문자 제거
    text = re.sub(r'\s+', ' ', text)  # 공백 정리
    return text.strip()

def extract_reviews_from_html(html, product_name):
    soup = BeautifulSoup(html, "lxml")
    review_list = soup.select("div.review_list_wrap ul.inner_list li")
    data = []

    for li in review_list:
        txt_tag = li.select_one("div.review_cont div.txt_inner")
        review_text_raw = txt_tag.get_text(strip=True) if txt_tag else None
        review_text = review_text_raw if review_text_raw else None

        poll_items = li.select("div.review_cont div.poll_sample dl.poll_type1 dd span.txt")
        발색력 = poll_items[0].get_text(strip=True) if len(poll_items) > 0 else None
        지속력 = poll_items[1].get_text(strip=True) if len(poll_items) > 1 else None
        발림성 = poll_items[2].get_text(strip=True) if len(poll_items) > 2 else None
        수분감 = poll_items[3].get_text(strip=True) if len(poll_items) > 3 else None

        score_tag = li.select_one("div.review_cont div.score_area span.review_point span.point")
        star_value = None
        if score_tag:
            style_val = score_tag.get("style", "")
            if "width:" in style_val:
                pct = float(style_val.split(":")[1].replace("%", "").strip())
                star_value = round(pct / 20, 1)

        if review_text and star_value is not None:
            data.append({
                "product_name": product_name,
                "star": star_value,
                "review": review_text,
                "발색력": 발색력,
                "지속력": 지속력,
                "발림성": 발림성,
                "수분감": 수분감
            })
    return data

def transform_reviews(html_pages):
    all_data = []
    for html, product_name in html_pages:
        extracted = extract_reviews_from_html(html, product_name)
        all_data.extend(extracted)
    df = pd.DataFrame(all_data)
    df['review'] = df['review'].apply(clean_text)
    return df

def load_reviews(df, filename="21_reviews_score.csv"):
    df.to_csv(filename, index=False, encoding="utf-8")

def crawl_paginated_reviews(url, option_text="21호/핑크베이지"):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["ko-KR", "ko"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    all_html_pages = []

    try:
        driver.get(url)
        time.sleep(3)
        driver.refresh()
        time.sleep(3)

        WebDriverWait(driver, 15).until_not(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.prd_recommend"), "고객님을 위한 상품추천중이에요")
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
        time.sleep(3)

        review_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#reviewInfo"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", review_tab)
        review_tab.click()
        time.sleep(3)

        try:
            all_option_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.sel_option.item.all"))
            )
            all_option_btn.click()
            time.sleep(3)
        except Exception as e:
            print("전체 상품옵션 버튼 클릭 실패:", e)

        try:
            option_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@class="txt" and contains(text(), "{option_text}")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", option_element)
            option_element.click()
            time.sleep(3)
        except Exception as e:
            print("옵션 선택 실패:", e)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.review_cont div.txt_inner"))
        )

        product_name = driver.find_element(By.CSS_SELECTOR, "div.review_cont p.item_option").text.strip()
        page_num = 1

        while True:
            print(f"페이지 {page_num} 수집 중...")
            html = driver.page_source
            all_html_pages.append((html, product_name))

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, f'div.pageing a[data-page-no="{page_num + 1}"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                next_button.click()
                time.sleep(5)
                page_num += 1
            except:
                try:
                    next_block = driver.find_element(By.CSS_SELECTOR, 'div.pageing a.next')
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_block)
                    next_block.click()
                    time.sleep(5)
                    page_num += 1
                except:
                    print("마지막 페이지 도달")
                    break

    finally:
        driver.quit()

    return all_html_pages

if __name__ == "__main__":
    test_url = "https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000178635"
    html_pages = crawl_paginated_reviews(test_url)
    df = transform_reviews(html_pages)
    load_reviews(df)
    print(df.head())
