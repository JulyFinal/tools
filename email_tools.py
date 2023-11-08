import feedparser
import pandas as pd
import apprise


def send_mail(link, title, content, tag):
    apobj = apprise.Apprise()
    apobj.add("mailtos://")
    apobj.notify(body=content, title=title, tag=tag)


def rss_read(rss_url: str):
    news_feed = feedparser.parse(rss_url)
    df_news_feed = pd.json_normalize(news_feed.entries)
    for _, row in df_news_feed.iterrows():
        print(row)
        send_mail(row.link, row.title, row.summary, row.tags)

    # print(df_news_feed)


if __name__ == "__main__":
    rss_read("https://www.hacg.me/wp/feed")
    # print(send_mail())
