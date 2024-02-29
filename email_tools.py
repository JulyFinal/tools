import feedparser
import pandas as pd
import apprise
from loguru import logger

from dotenv import dotenv_values

config = dotenv_values(".env")

user = config.get("email.name")
passwd = config.get("email.password")


def send_mail(link, title, content):
    apobj = apprise.Apprise()
    apobj.add(f"mailtos://{user}:{passwd}@outlook.com", tag="email")
    apobj.notify(body=content, title=title, tag="all")


def rss_read(rss_url: str):
    news_feed = feedparser.parse(rss_url)
    df_news_feed = pd.json_normalize(news_feed.entries)
    for _, row in df_news_feed.iterrows():
        try:
            send_mail(
                row.link,
                row.title,
                str(row.tags) + "\n" + str(row.summary),
            )
        except Exception as e:
            logger.error("以下内容失败")
            logger.error(row)
            logger.error(e)

    # print(df_news_feed)


if __name__ == "__main__":
    rss_read("https://www.hacg.me/wp/feed")
    # print(send_mail())
