import urllib.parse
import requests
import json
import re
from bs4 import BeautifulSoup, NavigableString

webclassurl = "https://rpwebcls.meijo-u.ac.jp"


def build_tree(wbc) -> dict:
    """
    時間割ページを起点にコース→セクション→コンテンツの3階層ツリーを構築する。
    PDFのダウンロードは行わず、download_query のみ保持する。
    """
    source = requests.get(wbc.url, cookies=wbc.cookies)
    soup = BeautifulSoup(source.text, "html.parser")
    schedule = soup.find(id="schedule-table")
    hrefs = schedule.find_all("a", href=True)

    seen_urls = set()
    courses = []
    for href in hrefs:
        url = href["href"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        course = _crawl_course(href, wbc.cookies)
        courses.append(course)

    return {"courses": courses}


def _parse_slot(text: str) -> str:
    """コース名文字列から曜日・限を抽出する。例: '(2026-前期-月1)' → '月1'"""
    m = re.search(r'\(\d{4}-[^-]+-([月火水木金土]\d+)', text)
    return m.group(1) if m else ""


def _getacs(source_text: str) -> str:
    soup = BeautifulSoup(source_text, "html.parser")
    exccode = soup.find("script").string
    return exccode.split('"')[1].replace("&amp;", "&")


def _crawl_course(href_el, cookies) -> dict:
    full_text = href_el.get_text()
    slot = _parse_slot(full_text)
    name_node = next(
        (s for s in href_el.children if isinstance(s, NavigableString) and s.strip()),
        None,
    )
    name = name_node.strip().lstrip("» ") if name_node else full_text.strip()
    course_url = webclassurl + href_el["href"]

    try:
        source = requests.get(course_url, cookies=cookies)
        acspath = _getacs(source.text)
        real_url = webclassurl + acspath
        source = requests.get(real_url, cookies=cookies)

        soup = BeautifulSoup(source.text, "html.parser")
        section_els = soup.find_all("section", class_="cl-contentsList_folder")
        sections = [_crawl_section(el, cookies) for el in section_els]

        return {"slot": slot, "name": name, "url": real_url, "sections": sections}
    except Exception as e:
        return {"slot": slot, "name": name, "url": course_url, "sections": [], "error": str(e)}


def _crawl_section(section_el, cookies) -> dict:
    title = section_el.find("h4", class_="panel-title").get_text().strip()
    content_els = section_el.find(class_="list-group").find_all(
        "section", class_="cl-contentsList_listGroupItem"
    )
    contents = [_crawl_content(el, cookies) for el in content_els]
    return {"name": title, "contents": contents}


def _crawl_content(content_el, cookies) -> dict:
    try:
        anchor = content_el.find("h4", class_="cm-contentsList_contentName").find("a")
        name = anchor.get_text().strip()
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(anchor["href"]).query)
        content_id = qs["set_contents_id"][0]

        content_url = (
            f"{webclassurl}/webclass/do_contents.php"
            f"?reset_status=1&set_contents_id={content_id}"
        )
        source = requests.get(content_url, cookies=cookies)
        acspath = _getacs(source.text)
        real_url = webclassurl + "/webclass/" + acspath
        source = requests.get(real_url, cookies=cookies)
        soup = BeautifulSoup(source.text, "html.parser")

        if "show_frame.php" in acspath:
            source = _skip_show_frame(soup, cookies)
            real_url = source.url
            soup = BeautifulSoup(source.text, "html.parser")

        path = urllib.parse.urlparse(real_url).path
        if path == "/webclass/qstn_frame.php":
            return _parse_assignment(soup, cookies, name, content_id)
        elif path == "/webclass/txtbk_frame.php":
            return _parse_textbook(soup, cookies, name, content_id)
        else:
            return {"id": content_id, "name": name, "type": "unknown", "url": real_url}

    except Exception as e:
        return {"name": "（取得エラー）", "type": "error", "reason": str(e)}


def _skip_show_frame(soup, cookies):
    """確認画面(show_frame)を2〜3ホップで通過して本来のコンテンツページを返す"""
    path = soup.find("frame", {"name": "contentsInfo"})["src"].replace("&amp;", "&")
    url = f"{webclassurl}/webclass/{path}"
    resp = requests.post(
        url,
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({"next": "%E9%96%8B%E5%A7%8B"}),
        cookies=cookies,
    )
    soup2 = BeautifulSoup(resp.text, "html.parser")
    url2 = webclassurl + soup2.find("script").string.split('"')[1].replace("&amp;", "&")
    resp2 = requests.get(url2, cookies=cookies)
    soup3 = BeautifulSoup(resp2.text, "html.parser")
    url3 = webclassurl + "/webclass/" + soup3.find("script").string.split('"')[1].replace("&amp;", "&")
    return requests.get(url3, cookies=cookies)


def _parse_assignment(soup, cookies, name, content_id) -> dict:
    """課題コンテンツ: question_url を download_query として保持"""
    answer_src = soup.find("frame", {"name": "answer"})["src"]
    ans_url = webclassurl + "/webclass/" + answer_src
    source = requests.get(ans_url, cookies=cookies)
    soup2 = BeautifulSoup(source.text, "html.parser")
    question_path = soup2.find("input", {"name": "question_url"})["value"]
    return {
        "id": content_id,
        "name": name,
        "type": "assignment",
        "download_query": question_path,
    }


def _classify_textbook_item(query: str, cookies) -> dict:
    """txtbk_show_text.php の内容を分類して item_type と追加情報を返す。
    - "pdf":        loadit.php リンクあり
    - "html":       <div class="contenttxt"> に本文テキスト
    - "attachment": 添付ファイルあり（リンク不明）
    """
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(query).query)
    file_val = qs.get("file", [""])[0]

    # file パラメータが非空なら PDF と判断（追加フェッチ不要）
    if file_val:
        return {"item_type": "pdf"}

    # file が空の場合はページ取得して本文を見る
    r = requests.get(webclassurl + query, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    contenttxt = soup.find("div", class_="contenttxt")
    if not contenttxt:
        return {"item_type": "html", "html_content": ""}

    text = contenttxt.get_text().strip()
    if "このページには添付ファイルがあります" in text:
        return {"item_type": "attachment"}

    # HTML / コード本文をそのまま保持
    return {"item_type": "html", "html_content": str(contenttxt)}


def _parse_textbook(soup, cookies, name, content_id) -> dict:
    """テキスト資料コンテンツ: 章ごとのアイテムリストを返す。
    各アイテムに item_type ("pdf" | "html" | "attachment") を付与する。"""
    chapter_src = soup.find("frame", {"name": "webclass_chapter"}).attrs["src"].replace("&amp;", "&")
    chapter_url = webclassurl + "/webclass/" + chapter_src
    resp = requests.get(chapter_url, cookies=cookies)
    soup2 = BeautifulSoup(resp.text, "html.parser")

    page_data = json.loads(soup2.find("script", id="json-data").get_text())
    text_urls = page_data["text_urls"]
    chapters = soup2.find_all("span", {"class": "size2 darkslategray"})

    items = []
    for i in range(len(text_urls)):
        chapter_name = chapters[i * 2].get_text() + "," + chapters[i * 2 + 1].get_text()
        query = text_urls[str(i + 1)]
        item = {"chapter": chapter_name, "query": query}
        item.update(_classify_textbook_item(query, cookies))
        items.append(item)

    return {"id": content_id, "name": name, "type": "textbook", "items": items}
