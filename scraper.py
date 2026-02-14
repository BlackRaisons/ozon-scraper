from playwright.sync_api import sync_playwright
import re
import random
from time import sleep
import json, csv
import os
from openpyxl import Workbook

STOP_PARSING = False

def stop_scraping():
    global STOP_PARSING
    STOP_PARSING = True


def save_data(all_data, save_path, file_format="json"):
    os.makedirs(save_path, exist_ok=True)
    
    if file_format == "json":
        file_path = os.path.join(save_path, "all_data.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

    elif file_format == "csv":
        file_path = os.path.join(save_path, "all_data.csv")
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
            writer.writeheader()
            writer.writerows(all_data)

    elif file_format == "xlsx":
        file_path = os.path.join(save_path, "all_data.xlsx")
        wb = Workbook()
        ws = wb.active
        ws.append(list(all_data[0].keys()))
        for row in all_data:
            ws.append(list(row.values()))
        wb.save(file_path)

    return file_path

def human_delay(min_sec=1, max_sec=3):
    sleep(random.uniform(min_sec, max_sec))

def random_mouse(page, moves=1):

    width = page.evaluate("() => window.innerWidth")
    height = page.evaluate("() => window.innerHeight")

    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)

    page.mouse.move(x, y)

    for _ in range(moves):

        new_x = random.randint(0, width - 1)
        new_y = random.randint(0, height - 1)

        page.mouse.move(
            new_x,
            new_y,
            steps=random.randint(8, 25)
        )

        sleep(random.uniform(0.05, 0.3))


def scrape_ozon(query: str, count_card: int, save_path: str, log_callback=None, file_format="json"):

    global STOP_PARSING

    urls = set()
    all_data = []

    if not query:
        raise ValueError("Запрос пустой")

    if not save_path:
        raise ValueError("Путь не указан")

    os.makedirs(save_path, exist_ok=True)

    def log(msg):
        if log_callback:
            log_callback(msg)

    log("Запуск браузера...")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )


        page = context.new_page()

        log("Открываем Ozon...")
        page.goto("https://www.ozon.ru/")

        human_delay(1, 2.5)

        log(f"Поиск: {query}")

        random_mouse(page)

        search = page.get_by_role("textbox", name="Искать на Ozon")

        human_delay(0.5, 1)
        search.click()

        human_delay(0.5, 1)
        search.fill(query)

        human_delay(0.5, 1.5)
        search.press("Enter")

        human_delay(1.5, 3)

        last_count = 0
        stuck_rounds = 0

        while len(urls) < count_card:
            
            if STOP_PARSING:
                log('\n\n\nПарсинг завершен дострочно\n\n\n')
                break

            end_block = page.locator("span").filter(has_text="Возможно, вам понравится")

            if end_block.count() > 0:
                log("Результаты закончились")
                break

            cards = page.locator(".tile-root")
            count = cards.count()

            for i in range(count):

                card = cards.nth(i)
                
                href = card.locator("a[target='_blank']").first.get_attribute("href")

                if not href:
                    continue

                link = "https://www.ozon.ru" + href

                if link in urls:
                    continue


                urls.add(link)

               
                prices = card.locator("span:has-text('₽')")
                price = prices.first.inner_text() if prices.count() > 0 else "Нет цены"
                old_price = prices.nth(1).inner_text() if prices.count() > 1 else "Нет старой цены"

                discount_locator = card.locator("span:has-text('%')")
                discount = discount_locator.first.inner_text() if discount_locator.count() > 0 else "Без скидки"

                rating_locator = card.get_by_text(re.compile(r"\d\.\d"))
                rating = rating_locator.first.inner_text() if rating_locator.count() > 0 else "Нет рейтинга"

                reviews_locator = card.locator("span:has-text('отзыв')")
                reviews = reviews_locator.first.inner_text() if reviews_locator.count() > 0 else "Нет отзывов"

                data = {
                    "link": link,
                    "price": price,
                    "old_price": old_price,
                    "discount": discount,
                    "rating": rating,
                    "reviews": reviews
                }

                all_data.append(data)


                log(f"[{len(all_data)}/{count_card}] Добавлена карточка:")
                log(f"Ссылка: {data['link']}")
                log(f"Цена: {data['price']}")
                log(f"Старая цена: {data['old_price']}")
                log(f"Скидка: {data['discount']}")
                log(f"Рейтинг: {data['rating']}")
                log(f"Отзывы: {data['reviews']}")
                log("") 

                if len(urls) >= count_card:
                    break


            if len(urls) == last_count:

                stuck_rounds += 1

                if stuck_rounds >= 3:
                    log("Новые карточки больше не загружаются")
                    break
            else:
                stuck_rounds = 0

            last_count = len(urls)

            random_mouse(page)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            human_delay(2, 3)


        file_path = save_data(all_data, save_path, file_format)


        log(f"Готово. Сохранено {len(all_data)} карточек")
        log(f"Файл: {file_path}")

        STOP_PARSING = False
        browser.close()
