import urllib.parse
import requests
from bs4 import BeautifulSoup
import webclass


def _loadit_href_to_pdf_url(href: str) -> str:
    """
    /webclass/loadit.php?lang=JAPANESE&file=%2Fwebclass%2Ftext%2F...
    → https://rpwebcls.meijo-u.ac.jp/webclass/text/...
    """
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
    file_path = qs["file"][0]  # parse_qs が URL デコード済み
    return webclass.webclassurl + file_path


def _find_loadit_href(html_text: str) -> str | None:
    """HTML から /webclass/loadit.php へのリンクを返す。なければ None"""
    soup = BeautifulSoup(html_text, "html.parser")
    for a in soup.find_all("a", href=True):
        if "/webclass/loadit.php" in a["href"]:
            return a["href"]
    return None


def getfiles(query: str, cookies, filepath: str):
    """
    query: crawler が保持する download_query / item.query (URL パス+クエリ文字列)
    """
    if "/webclass/loadit.php" in query:
        # 課題PDF: loadit.php の file パラメータから直接 PDF URL を構築
        pdf_url = _loadit_href_to_pdf_url(query)
        r = requests.get(pdf_url, cookies=cookies)
        if r.content[:4] != b"%PDF":
            raise Exception(f"PDFが返りませんでした (status={r.status_code})")
        with open(filepath, "wb") as f:
            f.write(r.content)
        return

    if "/webclass/txtbk_show_text.php" in query:
        # テキスト資料: HTMLページから loadit.php リンクを取り出して PDF URL を構築
        r1 = requests.get(webclass.webclassurl + query, cookies=cookies)
        href = _find_loadit_href(r1.text)
        if not href:
            raise Exception("PDFリンクが見つかりませんでした（資料未公開の可能性があります）")
        pdf_url = _loadit_href_to_pdf_url(href)
        r2 = requests.get(pdf_url, cookies=cookies)
        if r2.content[:4] != b"%PDF":
            raise Exception(f"PDFが返りませんでした (status={r2.status_code})")
        with open(filepath, "wb") as f:
            f.write(r2.content)
        return

    raise Exception(f"PDFが存在しないコンテンツです")
