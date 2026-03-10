import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.cache import cache


def fetch_content(url: str) -> tuple[str, str, datetime | None]:
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        content_div = soup.find("div", id="story_body_content")
        paragraphs = content_div.find_all("p") if content_div else []
        content = "\n".join(p.text.strip()
                            for p in paragraphs if p.text.strip())

        author_div = soup.find("div", class_="shareBar__info--author")
        publish_time = None
        author = ""
        if author_div:
            time_str = author_div.find(
                "span").text.strip()  # "2026-03-08 10:50"
            publish_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            author = author_div.get_text().replace(time_str, "").strip()
        return content, author, publish_time

    except Exception as e:
        print(f"爬取內文失敗 {url}:{e}")
        return "", "", None


def fetch_nba_news_list(latest_time: datetime | None) -> list[dict]:
    try:
        res = requests.get("https://tw-nba.udn.com/nba/index")

        soup = BeautifulSoup(res.text, "html.parser")
        dl = soup.find(id="news_list_body").find("dl")
        results = []

        for dt in dl.find_all("dt"):
            a = dt.find("a")
            if not a:
                continue

            title = a.find("h3").text.strip()
            url = a["href"]
            summary = a.find("p").text.strip()
            img = a.find("img")["src"]
            content, author, publish_time = fetch_content(url)

            # 已經爬過的文章就不爬了
            if latest_time is not None and publish_time is not None and latest_time >= publish_time:
                break

            results.append({
                "title": title,
                "url": url,
                "summary": summary,
                "img": img,
                "content": content,
                "publish_time": publish_time,
                "author": author
            })

        print(f"爬取完成，共 {len(results)} 篇新文章")
        return results

    except Exception as e:
        print(f"爬取列表失敗 {e}")
        return []


def save_to_db(articles: list[dict]) -> None:
    from news.models import Article
    import pytz

    tz = pytz.timezone("Asia/Taipei")
    saved = 0
    for data in articles:
        publish_time = data["publish_time"]
        if publish_time is not None and publish_time.tzinfo is None:
            publish_time = tz.localize(publish_time)

        _, created = Article.objects.get_or_create(
            url=data["url"],
            defaults={
                "title": data["title"],
                "summary": data["summary"],
                "img": data["img"],
                "content": data["content"],
                "author": data["author"],
                "publish_time": publish_time,
            },
        )
        if created:
            saved += 1
    if saved > 0:
        cache.delete_pattern("articles:page:*")
        _broadcast_update(saved)

    print(f"儲存完成，新增 {saved} 篇")


def _broadcast_update(count: int) -> None:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from news.consumers import NEWS_GROUP

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        NEWS_GROUP,
        {"type": "news.update", "count": count},
    )


def run() -> None:
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from news.models import Article

    latest = Article.objects.order_by("-publish_time").first()
    latest_time = None
    if latest and latest.publish_time:
        # strip tz for comparison with naive datetimes from parser
        latest_time = latest.publish_time.replace(tzinfo=None)

    articles = fetch_nba_news_list(latest_time)
    if articles:
        save_to_db(articles)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        # 直接執行（不寫DB），方便本地測試
        now = datetime(2026, 3, 8)
        fetch_nba_news_list(now)
