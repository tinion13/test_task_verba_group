import time
import json
import math

import undetected_chromedriver as uc


options = uc.ChromeOptions()

def get_url(
    page: int, 
    query: str,
):
    url = (
        f"https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?"
        f"ab_testing=false"
        f"&appType=1"
        f"&curr=rub"
        f"&dest=-1257786"
        f"&hide_vflags=4294967296"
        f"&lang=ru"
        f"&page={page}"
        f"&query={query}"
        f"&resultset=catalog"
        f"&sort=popular"
        f"&spp=30"
        f"&suppressSpellcheck=false"
    )
    
    return url


def get_articles_from_query(query: str, file_name: str):
    def load_page(driver, page_num: int, delay: int) -> dict:
        driver.get(get_url(page_num, query))
        time.sleep(delay)
        raw = driver.find_element("tag name", "body").text
        return json.loads(raw)

    def extract_ids(response: dict) -> list:
        return [
            product["id"]
            for product in response.get("products", [])
            if product.get("id") is not None
        ]

    with uc.Chrome(options=options, version_main=146, use_subprocess=True) as driver:
        first_page = load_page(driver, 1, 20)
        articles = extract_ids(first_page)

        total = first_page.get("total", 0)
        pages = math.ceil(total / 100)
        print(f"Total articles: {total} | Pages: {pages}")

        for page_num in range(2, pages + 1):
            response = load_page(driver, page_num, 8)
            articles.extend(extract_ids(response))

        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(articles, file, indent=4, ensure_ascii=False)
    