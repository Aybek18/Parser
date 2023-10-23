import time
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pandas.core.frame import DataFrame


@dataclass
class BybitParser:
    url = "https://announcements.bybit.com/en-US/?category=&page=1"
    user_agent = UserAgent()

    def get_webpage(self, url: str) -> bytes:
        """ Получаем данные с сайта """
        try:
            headers = {
                'User-Agent': self.user_agent.random
            }
            response = requests.get(url, headers=headers)
            return response.content
        except requests.exceptions.RequestException as e:
            print("Ошибка при запросе:", e)

    @staticmethod
    def parse_news(web_page: bytes) -> list:
        """ Парсим новости по полям """
        soup = BeautifulSoup(web_page, "html.parser")

        news_elements = soup.find_all("a", class_="no-style")

        news_list = []
        for news_item in news_elements:
            news_title = news_item.find("div",
                                        class_="ant-typography ant-typography-ellipsis article-item-title").span.text
            news_link = "https://announcements.bybit.com/" + news_item["href"]
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            news_list.append([current_time, news_title, news_link])
        return news_list

    def save_data(self) -> None:
        """ Проверка на уникальность новостей по Title и сохранение в csv файл """
        web_page = self.get_webpage(url=self.url)
        news_list = self.parse_news(web_page=web_page)

        existing_news = self.get_csv()

        new_news_df = pd.DataFrame(news_list, columns=["Time", "Title", "Link"])
        new_news_df = new_news_df[~new_news_df["Title"].isin(existing_news["Title"])]
        if not new_news_df.empty:
            existing_news = pd.concat([existing_news, new_news_df], ignore_index=True)
            existing_news.to_csv("bybit_news.csv", mode="w", index=False, encoding="utf-8")

        print(f"Сохранено {new_news_df['Title'].nunique()} новостей.")

    @staticmethod
    def get_csv() -> DataFrame:
        """Получаем уже существующие данные с csv файла, либо создаем этот файл если нет."""
        try:
            existing_news = pd.read_csv("bybit_news.csv", encoding="utf-8")
        except FileNotFoundError:
            existing_news = pd.DataFrame(columns=["Time", "Title", "Link"])
        return existing_news


if __name__ == "__main__":
    while True:
        # TODO Здесь конечно надо отрефакторить код. Можно по другому реализовать и добавить логирование
        BybitParser().save_data()
        time.sleep(1)
