from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

@app.route("/rss/infobae-colombia")
def infobae_rss():
    url = "https://www.infobae.com/colombia/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    items = ""
    for article in soup.select("a.caja-nota")[:10]:
        title = article.get("title") or article.text.strip()
        link = article.get("href")
        if link and not link.startswith("http"):
            link = "https://www.infobae.com" + link
        items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
        </item>
        """

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>Infobae Colombia</title>
            <link>{url}</link>
            <description>Noticias de la sección Colombia - Infobae</description>
            {items}
        </channel>
    </rss>"""
    
    return Response(rss_feed, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
