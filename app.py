from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

app = Flask(__name__)

CACHE_FILE = "infobae_colombia_rss.xml"
CACHE_TIME = 6 * 60 * 60  # 6 horas

def get_article_content(link):
    try:
        r = requests.get(link, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")

        article_body = soup.select_one("div.article-body") or soup.select_one("div[data-type='articleBody']")
        if not article_body:
            return "Contenido no disponible"

        # Imagen destacada (si existe)
        img_tag = soup.select_one("figure img")
        img_html = f'<img src="{img_tag["src"]}" alt="Imagen destacada"><br>' if img_tag else ""

        return img_html + str(article_body)
    except Exception as e:
        print(f"Error al obtener contenido de {link}: {e}")
        return "Contenido no disponible"

def generate_rss():
    url = "https://www.infobae.com/colombia/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    items = ""
    for a_tag in soup.select("a.story-card-ctn")[:10]:
        link = a_tag.get("href")
        if link and not link.startswith("http"):
            link = "https://www.infobae.com" + link

        title_tag = a_tag.select_one("h2.story-card-hl")
        title = title_tag.get_text(strip=True) if title_tag else "Sin título"

        content = get_article_content(link)

        items += f"""
        <item>
            <title><![CDATA[{title}]]></title>
            <link>{link}</link>
            <description><![CDATA[{content}]]></description>
            <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            <guid>{link}</guid>
        </item>
        """

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>Infobae Colombia</title>
            <link>{url}</link>
            <description>Noticias de la sección Colombia - Infobae</description>
            <language>es</language>
            {items}
        </channel>
    </rss>"""

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(rss_feed)

def is_cache_expired():
    if not os.path.exists(CACHE_FILE):
        return True
    last_modified = os.path.getmtime(CACHE_FILE)
    return (time.time() - last_modified) > CACHE_TIME

@app.route("/rss/infobae-colombia")
def infobae_rss():
    if is_cache_expired():
        print("⏳ Cache expirada. Generando nuevo RSS.")
        generate_rss()
    else:
        print("✅ Usando cache actual.")

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return Response(f.read(), mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
