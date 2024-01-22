import feedparser
import pandas as pd
import apprise

user = ...
passwd = ...


def send_mail(link, title, content):
    apobj = apprise.Apprise()
    apobj.add(f"mailtos://{user}:{passwd}@outlook.com", tag="email")
    apobj.notify(body=content, title=title, tag="all")


def rss_read(rss_url: str):
    news_feed = feedparser.parse(rss_url)
    df_news_feed = pd.json_normalize(news_feed.entries)
    for _, row in df_news_feed.iterrows():
        send_mail(row.link, row.title, row.tags + "\n" + row.summary)

    # print(df_news_feed)


if __name__ == "__main__":
    rss_read("https://www.hacg.me/wp/feed")
    # print(send_mail())
