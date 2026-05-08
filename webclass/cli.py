"""
WebClass CLI — Wails GUI から subprocess で呼び出すエントリーポイント。

使い方:
  python cli.py tree                              # コース構造をJSON出力
  python cli.py download --query <q> --path <p>  # PDF1件ダウンロード
  python cli.py check-credentials                 # 認証情報の存在確認 (exit 0:あり / 1:なし)
  python cli.py set-credentials --userid <id> --password <pass>  # 認証情報を保存
"""

import argparse
import json
import sys
import os
import io

# webclass/ を常に基準ディレクトリにする（subprocess 呼び出し時のパス解決のため）
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class _SuppressStdout:
    """認証ログなど既存コードの stdout 出力を JSON 出力と混在させないために一時抑制する"""

    def __enter__(self):
        self._orig = sys.stdout
        sys.stdout = io.StringIO()
        return self

    def __exit__(self, *_):
        sys.stdout = self._orig


def _login():
    import webclass
    import settings as s

    try:
        userdata = s.decodebydict()
    except Exception:
        _error("認証情報が見つかりません。先に set-credentials を実行してください。")

    with _SuppressStdout():
        wbc = webclass.webclass(userdata["userid"], userdata["password"])
    return wbc


def _error(msg: str, code: int = 1):
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


def cmd_tree(_args):
    import crawler

    wbc = _login()
    tree = crawler.build_tree(wbc)
    print(json.dumps(tree, ensure_ascii=False))


def cmd_download(args):
    import filedownload

    wbc = _login()
    os.makedirs(os.path.dirname(os.path.abspath(args.path)), exist_ok=True)
    with _SuppressStdout():
        filedownload.getfiles(args.query, wbc.cookies, args.path)
    print(json.dumps({"ok": True, "path": args.path}, ensure_ascii=False))


def cmd_check_credentials(_args):
    import settings as s

    try:
        s.decodebydict()
        sys.exit(0)
    except Exception:
        sys.exit(1)


def cmd_set_credentials(args):
    import settings as s

    keyfile = json.dumps({"userid": args.userid, "password": args.password})
    s.encode(keyfile)
    print(json.dumps({"ok": True}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="WebClass CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("tree", help="コース構造をJSON出力")

    dl = sub.add_parser("download", help="PDFをダウンロード")
    dl.add_argument("--query", required=True, help="download_query文字列")
    dl.add_argument("--path", required=True, help="保存先ファイルパス")

    sub.add_parser("check-credentials", help="認証情報の存在確認")

    sc = sub.add_parser("set-credentials", help="認証情報を保存")
    sc.add_argument("--userid", required=True)
    sc.add_argument("--password", required=True)

    args = parser.parse_args()

    commands = {
        "tree": cmd_tree,
        "download": cmd_download,
        "check-credentials": cmd_check_credentials,
        "set-credentials": cmd_set_credentials,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
