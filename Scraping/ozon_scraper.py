import os
import re
import json
import csv
import random
from time import sleep
from openpyxl import Workbook
from playwright.sync_api import sync_playwright


class OzonScraper:
    def __init__(self, query, count, save_path, log_callback=None, file_format="json"):
        self.query = query
        self.count = count
        self.save_path = save_path
        self.log_callback = log_callback
        self.file_format = file_format
        self.stop_flag = False
        self.urls = set()
        self.all_data = []

        if not self.query:
            raise ValueError("Запрос пустой")
        if not self.save_path:
            raise ValueError("Путь не указан")
        os.makedirs(self.save_path, exist_ok=True)

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def human_delay(self, min_sec=1, max_sec=3):
        sleep(random.uniform(min_sec, max_sec))

    def random_mouse(self, page, moves=1):
        width = page.evaluate("() => window.innerWidth")
        height = page.evaluate("() => window.innerHeight")
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        page.mouse.move(x, y)
        for _ in range(moves):
            new_x = random.randint(0, width - 1)
            new_y = random.randint(0, height - 1)
            page.mouse.move(new_x, new_y, steps=random.randint(8, 25))
            sleep(random.uniform(0.05, 0.3))

    def save_data(self):
        os.makedirs(self.save_path, exist_ok=True)
        file_path = os.path.join(self.save_path, f"all_data.{self.file_format}")

        if self.file_format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.all_data, f, indent=4, ensure_ascii=False)

        elif self.file_format == "csv":
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.all_data[0].keys())
                writer.writeheader()
                writer.writerows(self.all_data)

        elif self.file_format == "xlsx":
            wb = Workbook()
            ws = wb.active
            ws.append(list(self.all_data[0].keys()))
            for row in self.all_data:
                ws.append(list(row.values()))
            wb.save(file_path)

        return file_path

    def stop_scraping(self):
        self.stop_flag = True

    def scrape(self):
        self.log("Запуск браузера...")
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
            page.goto("https://www.ozon.ru/")
            self.human_delay(1, 2.5)

            self.log(f"Поиск: {self.query}")
            self.random_mouse(page)

            search = page.get_by_role("textbox", name="Искать на Ozon")
            self.human_delay(0.5, 1)
            search.click()
            self.human_delay(0.5, 1)
            search.fill(self.query)
            self.human_delay(0.5, 1.5)
            search.press("Enter")
            self.human_delay(1.5, 3)

            last_count = 0
            stuck_rounds = 0

            while len(self.urls) < self.count:
                if self.stop_flag:
                    self.log("Парсинг завершен досрочно")
                    break

                end_block = page.locator("span").filter(has_text="Возможно, вам понравится")
                if end_block.count() > 0:
                    self.log("Результаты закончились")
                    break

                cards = page.locator(".tile-root")
                count = cards.count()

                for i in range(count):
                    card = cards.nth(i)
                    href = card.locator("a[target='_blank']").first.get_attribute("href")
                    if not href:
                        continue

                    link = "https://www.ozon.ru" + href
                    if link in self.urls:
                        continue

                    self.urls.add(link)
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
                    self.all_data.append(data)

                    self.log(f"[{len(self.all_data)}/{self.count}] Добавлена карточка: {link}")

                    if len(self.urls) >= self.count:
                        break

                if len(self.urls) == last_count:
                    stuck_rounds += 1
                    if stuck_rounds >= 3:
                        self.log("Новые карточки больше не загружаются")
                        break
                else:
                    stuck_rounds = 0

                last_count = len(self.urls)
                self.random_mouse(page)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.human_delay(2, 3)

            file_path = self.save_data()
            self.log(f"Готово. Сохранено {len(self.all_data)} карточек")
            self.log(f"Файл: {file_path}")
            browser.close()





