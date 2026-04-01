import json
import time
from random import randint

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml import html

options = uc.ChromeOptions()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})


def get_url(article: int):
    return f"https://www.wildberries.ru/catalog/{article}/detail.aspx"


def collect_card_and_details(driver, wait_seconds: int, article: str) -> tuple[dict | None, dict | None]:

    deadline = time.time() + wait_seconds
    processed_request_ids = set()
    card = None
    details = None
    
    while time.time() < deadline:
        log_entries = driver.get_log("performance")
        for entry in log_entries:
            try:
                message = json.loads(entry["message"])["message"]
                method = message.get("method")
                params = message.get("params", {})
                
                if method != "Network.responseReceived":
                    continue

                response = params.get("response", {})
                request_id = params.get("requestId")
                response_url = response.get("url", "")

                if request_id in processed_request_ids:
                    continue

                processed_request_ids.add(request_id)

                if article not in response_url:
                    continue
                

                if (card_have_value:="card.json" in response_url) or "detail?" in response_url:
                    body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    response_data = json.loads(body['body'])
                    
                    if card_have_value:
                        card = response_data
                    else:
                        details = response_data
                    
                if card and details:
                    return card, details.get("products", [None, ])[0]

            except Exception:
                continue

        time.sleep(.3)
    
    return card, details


def parse_articles_to_data(
    articles_file_json: str,
    output_file_json: str,
    limit_items: int | None,
):
    with open(articles_file_json, encoding="utf-8") as file:
        articles = json.load(file)

    results = []
    with uc.Chrome(options=options, version_main=146, use_subprocess=True) as driver:
        driver.execute_cdp_cmd("Network.enable", {})

        for article in articles if limit_items is None else articles[:limit_items]:
            url = get_url(article)

            driver.get(url)
            wait = WebDriverWait(driver, 20)
            conditions = [
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "productPageContent")]')),
            ]
            wait.until(EC.all_of(*conditions))
            
            card, details = collect_card_and_details(driver, 10, str(article))
            if details:
                name = details.get("name")
                description = card.get("description") if card else None
                characteristics = card.get("options") if card else None
                seller_name = details.get("supplier")
                seller_url = f"https://www.wildberries.ru/seller/{details['supplierId']}" if details.get("supplierId") else None
                sizes = [
                    {
                        "name": size.get("name"),
                        "price": size["price"].get("product") if size.get("price") else None,
                        "remains": size["stocks"][0].get("qty") if size.get("stocks") else None,
                    } 
                    for size in details["sizes"]
                ] if details.get("sizes") else None

                rating = details.get("nmReviewRating", None)
                number_reviews = details.get("nmFeedbacks", None)
            else:
                name = None
                description = None
                characteristics = None
                seller_name = None
                seller_url = None
                sizes = None
                rating = None
                number_reviews = None
            
            page_source = driver.page_source
            tree = html.fromstring(page_source)
            
            images_urls = ",".join(tree.xpath('//div[contains(@class, "productPageContent")]//div[contains(@class, "swiper-wrapper")]//img/@src'))
            
            results.append({
                "url": url,
                "article": article,
                "name": name,
                "description": description,
                "images_urls": images_urls,
                "characteristics": characteristics,
                "seller_name": seller_name,
                "seller_url": seller_url,
                "sizes": sizes,
                "rating": rating,
                "number_reviews": number_reviews,
            })

            time.sleep(randint(1, 20) / 10)

    with open(output_file_json, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
