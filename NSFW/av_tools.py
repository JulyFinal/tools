import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import time
from loguru import logger
from typing import Union, List
from dataclasses import dataclass
import pathlib

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session

from rich import print

from basic import AVMeta

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}


@dataclass
class av:
    avid: str
    title: str
    date: Union[str, None]
    actor: Union[List[str], str]
    tags: Union[List[str], None]
    cover: Union[str, None]
    actor_cover: Union[List[str], str, None]

    def to_format_name(self, seq=" | "):
        actor = self.actor
        if isinstance(actor, list):
            actor = ",".join(actor)

        return actor + seq + self.avid + seq + self.title


def get_list(s, e):
    """
    爬取no.1 play list
    """

    def get_info(html_raw):
        res = []
        date_res = []

        soup = BeautifulSoup(html_raw, "lxml")
        content = soup.get_text()

        content_res = re.findall(
            r"FC2-PPV[-−]\d+|FC[-−]\d+|[a-z]{3,}[-−]\d{3,}", content, re.IGNORECASE
        )
        res += content_res

        content_date_res = re.findall(r"\d{4}/\d{2}/\d{2}", content)
        date_res += content_date_res

        links = soup.select("a")
        for link in links:
            if link["href"]:
                link_res = re.findall(r"spcode\=(.*?)\&", link["href"])
                res += link_res
        res = list(set(res))
        date_res = list(set(date_res))
        return res, date_res

    def get_content(url):
        headers = {
            "Cookie": "HZ1J_2846_saltkey=9T8SJv1j; HZ1J_2846_lastvisit=1690871568; playno1=playno1Cookie; HZ1J_2846_sid=X74vx7; playno1_referer=%2Farticle-39849-1.html; HZ1J_2846_secqaaSX74vx70=e9b83me%2BIS4HoGeT%2FiScSTbxCrAeNhppWMiYEKVfUHig2tHslsYsHa%2BJGO%2FtxoBrgncBrDDFK%2BfCK0JRjNm4LVObjZd3xaN8o6xRqgYIMM75udsLodWzABsY; HZ1J_2846_lastact=1691489341%09portal.php%09view",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0",
            "Host": "www.playno1.com",
        }
        response = requests.get(url, headers=headers, proxies=proxies)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "lxml")
        title = soup.find("title").get_text()
        content = soup.find("td", {"id": "article_content"})
        res, date_res = get_info(content.prettify())
        return title, res, date_res

    av_res = []

    for i in range(s, e + 1):
        url = f"http://www.playno1.com/article-{i}-1.html"
        try:
            logger.info("current article is :" + url)
            title, avs, date = get_content(url)
            logger.info(f"{avs}" + ", " + f"{date}")
            if avs:
                # if len(res) == len(date):
                #     for i in zip(res, date):
                #         res.append([title, i[0], i[1]])
                # else:
                #     for i in res:
                #         res.append([title, i, date])
                av_res.append([title, avs, date])

            else:
                logger.warning("PASSED! " + "TITLE: " + title + " URL: " + url)
        except Exception as e:
            logger.error(url + "! error !" + str(e))
    return av_res


def nyaa_search(query):
    search_url = f"https://sukebei.nyaa.si/?q={query}&f=0&c=0_0"

    response = requests.get(search_url, proxies=proxies)
    soup = BeautifulSoup(response.content, "lxml")

    headers = [
        "Category",
        "Name",
        "Link",
        "Size",
        "Date",
        "Seeders",
        "Leechers",
        "Completed downloads",
    ]

    try:
        html_table = soup.find("table").prettify()
        table_soup = BeautifulSoup(html_table, "lxml")
        values = []
        for idx, tr in enumerate(table_soup.find_all("tr")):
            if idx != 0:
                tds = []
                for idx, td in enumerate(tr.find_all("td")):
                    if idx in [0, 1]:
                        cell = td.find("a").get("title")
                    elif idx == 2:
                        cell = [a.get("href") for a in td.find_all("a")][1]
                    else:
                        cell = td.get_text().strip()
                    tds.append(cell)
                values.append(tds)

        df = pd.DataFrame(values, columns=headers)
        return df
    except Exception:
        logger.warning(query + " ==> NOT FOUND RES!")
        return pd.DataFrame([], columns=headers)


@logger.catch
def get_meta_data(query):
    # aiav
    base_url = f"https://aiav.app/episode/{query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0",
    }
    response = requests.get(base_url, headers=headers, proxies=proxies)

    soup = BeautifulSoup(response.content, "lxml")
    print(soup)

    avid = soup.select_one("h5.MuiTypography-h5").get_text()
    if img := soup.find(
        "img", src=re.compile("cover")
    ):  # soup.select_one("img")["src"]
        av_img = img["src"]
    else:
        av_img = None
    title = soup.select_one("p.MuiTypography-body1").get_text()
    date = soup.select_one("time").get_text()
    tags = [i.get_text() for i in soup.select("span.MuiChip-label")]
    actor = [i.get_text() for i in soup.select("p.css-13ldsdq")]

    actor_imgs = [i["src"] for i in soup.find_all("img", herf=re.compile("actress"))]

    res = av(avid, title, date, actor, tags, av_img, actor_imgs)

    return res


@logger.catch
def get_magnet(query):
    query = re.sub(r"\-C$", "", query, re.IGNORECASE)
    table = nyaa_search(query)
    if table.empty:
        return None
    else:
        table[["Seeders", "Leechers", "Completed downloads"]] = table[
            ["Seeders", "Leechers", "Completed downloads"]
        ].astype("int64")
        ids = [
            table["Seeders"].idxmax(),
            table["Leechers"].idxmax(),
            table["Completed downloads"].idxmax(),
        ]
        i = sorted(ids)[len(ids) // 2]
        magnet = table.loc[i, "Link"]
        return magnet


def av_rename_func(av_path, av_library_path):
    al = pd.read_pickle(av_library_path)
    for file_name in os.listdir(av_path):
        av_id = re.sub(r"\.(mp4|mkv)\n", "", file_name)
        print(al.loc[al["name"] == av_id])


def format_av_name(av_file):
    path = pathlib.Path(av_file)
    name = re.sub(r"\.(mp4|mkv)\n", "", path.name)
    name = clear_name(name)
    try:
        meta_data = get_meta_data(name)
        format_name = meta_data.to_format_name()
        final_name = format_name + path.suffix
        print(f"mv {av_file} {final_name}")
    except:
        print(av_file)
    # return final_name


def clear_name(av_name):
    av_name = re.sub("^hhd800.com@", "", av_name)
    av_name = re.sub("-[Cc]$", "", av_name)
    return av_name.upper()


def group_res(res):
    final_res = []

    for avs, times in res:
        times_len = len(times)
        if times_len == 0:
            for av in avs:
                final_res.append(AVMeta(av_id=clear_name(av)))
        else:
            c_time = max(times, key=lambda x: time.strptime(x, "%Y/%m/%d"))
            for av in avs:
                final_res.append(AVMeta(av_id=clear_name(av), publish_time=c_time))
    return final_res


def avlist_group(start):
    end = get_playav_last_id()
    print(f"{end:=}")
    avlist = get_list(start, end + 1)
    return group_res(
        [[cell for idx, cell in enumerate(row) if idx > 0] for row in avlist]
    )


def get_playav_last_id():
    rss_url = "https://rsshub.app/playno1/av"
    response = requests.get(rss_url, proxies=proxies)
    id = re.search(
        "\<link\>http\:\/\/www\.playno1\.com/article-(\d+)-1\.html\<\/link\>",
        str(response.content),
    ).group(1)
    return int(id)


def append_data_use_id(arc_id):
    av_list = avlist_group(arc_id + 1)
    with Session(engine) as session:
        all_data = session.query(AVMeta).all()
        av_id_list = [av.av_id for av in all_data]
        append_list = []
        for av in av_list:
            if av.av_id not in av_id_list:
                append_list.append(av)
        logger.info(append_list)
        session.add_all(append_list)
        session.commit()


def after_today_magnet():
    res = []
    with Session(engine) as session:
        all_data = (
            session.query(AVMeta)
            .filter(
                and_ (AVMeta.publish_time == None, AVMeta.favorites == None)
                | and_(
                    AVMeta.publish_time <= time.strftime("%Y/%m/%d", time.localtime()),
                    AVMeta.favorites == None,
                )
            )
            .all()
        )

        for av in all_data:
            if magnet_url := get_magnet(av.av_id):
                res.append(magnet_url)
                session.query(AVMeta).filter(AVMeta.av_id == av.av_id).update(
                    {"favorites": False}
                )
        session.commit()
    return res


if __name__ == "__main__":
    engine = create_engine("sqlite:///final.db", echo=True)
    # append_data_use_id(40535 + 1)
    print("\n".join(after_today_magnet()))
