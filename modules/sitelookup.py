import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

history_file_path = "/home/nsl-spbstu-news-bot/data/news_history.json"

def month_prettify(month: str) -> str:
    months = {
        "Янв": "01",
        "Фев": "02",
        "Мар": "03",
        "Апр": "04",
        "Май": "05",
        "Июн": "06",
        "Июл": "07",
        "Авг": "08",
        "Сен": "09",
        "Окт": "10",
        "Ноя": "11",
        "Дек": "12",
    }
    return months[month]

def load_history():
    if os.path.exists(history_file_path):
        try:
            with open(history_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_history(history):
    with open(history_file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def lookup_for_updates() -> tuple[list, str]:
    headers = {
        "Accept": "text/html",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }

    req = requests.get("https://nsl.spbstu.ru/news/", headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    current_news = []

    for new in soup.find_all('div', class_='news-list-item__card'):
        tmp_day = new.find('div', class_='news-list-item__day').get_text()
        day = tmp_day if len(tmp_day) == 2 else "0" + tmp_day
        month = month_prettify(new.find('div', class_='news-list-item__month').get_text())
        year = soup.find('div', class_='news-list-item__year').get_text()

        title_raw = new.find('a', class_='news-list-item__title')
        title = title_raw.get_text().strip()
        link = title_raw.get('href')

        news_item = {
            "date": f"{day}.{month}.{year}",
            "title": title,
            "link": link,
            "timestamp": datetime.now().isoformat()
        }
        current_news.append(news_item)

    history = load_history()
    
    new_news = []
    seen_links = set(item['link'] for item in history)
    
    for news_item in current_news:
        if news_item['link'] not in seen_links:
            new_news.append(news_item)
        else:
            break
    
    for item in new_news:
        if item['date'] == '' or item['title'] == '' or item['link'] == '':
            return [], f"Возникла ошибка при получении данных\n```{item=}```"
    
    if new_news:
        updated_history = new_news + history
        updated_history = updated_history[:100]
        save_history(updated_history)
    
    print(f"Найдено новых новостей: {len(new_news)}")
    
    if not new_news:
        return [], "Обновлений нет"
    
    return list(reversed(new_news)), ""

def show_history():
    history = load_history()
    print(f"Всего в истории: {len(history)} новостей")
    for i, item in enumerate(history[:5], 1):  # показываем первые 5
        print(f"{i}. {item['date']} - {item['title']}")

