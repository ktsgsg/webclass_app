# WebClass GUI 実装進捗

## 概要
WebClass（名城大学LMS）の資料・課題をネイティブデスクトップアプリで閲覧・操作できるようにする。
技術スタック: Python（クローラー） + Go（Wailsバックエンド） + Svelte（フロントエンド）

## アーキテクチャ方針
- 既存の Python クローラー（`webclass/`）はそのまま流用
- Wails の Go バックエンドが Python を subprocess で起動
- Python は JSON を stdout に出力し、Go がパースして Svelte に渡す
- 認証情報は既存の `settings.py`（Fernet 暗号化）を継続使用

## 実装ログ

---

### [Phase 1] Python CLI 整備
**ブランチ:** `feature/python-cli`
**PR:** https://github.com/ktsgsg/webclass_app/pull/1
**目的:** Wails から subprocess で呼べる CLI を整備

**実施内容:**
- [x] `crawler.py` 新規作成: `build_tree()` でダウンロードなしのJSON ツリー構築
- [x] `cli.py` 新規作成: argparse で tree / download / check-credentials / set-credentials
- [x] `_SuppressStdout` で既存コードの stdout 汚染を遮断

**結果:** ✅ 完了 (コミット: 8d682f6)

---

### [Phase 2-4] Wails GUI 初期実装
**ブランチ:** `feature/wails-gui`
**目的:** Wails + Svelte のデスクトップアプリ基本実装

**実施内容:**
- [x] `wails init -n webclass-gui -t svelte`
- [x] `app.go`: Go バインディング実装（CheckCredentials / SetCredentials / GetTree / DownloadPDF）
- [x] `App.svelte`: ログイン → ローディング → メインレイアウトの状態管理
- [x] `lib/Login.svelte`: 初回認証情報入力フォーム
- [x] `lib/TreePanel.svelte`: 時間割→コース→セクション→コンテンツの3階層ツリー
- [x] `lib/ContentPanel.svelte`: textbook (章リスト) / assignment (PDF) / error 表示

**結果:** ✅ ビルド成功

---

## 既知の課題・注意事項
- WebClass の JS リダイレクト（偽リダイレクト）は `getacs()` で処理済み
- 課題提出は multipart POST（詳細調査が必要）
- 認証情報は `key.key` / `userdata.txt` に保存（.gitignore 済み）
- `structure.json` も .gitignore 済み

---

### [Phase 5] クローラーバグ修正
**ブランチ:** `main`
**目的:** ツリー展開できない根本原因の修正

**発見した問題:**
1. **URL二重パス**: `_crawl_course` の `real_url = webclassurl + "/webclass/" + acspath` が
   `acspath` にすでに `/webclass/course.php/...` が含まれるため
   `https://rpwebcls.meijo-u.ac.jp/webclass//webclass/course.php/...` となり 404 → `sections: []`
2. **コース名にバッジテキスト混入**: `href_el.get_text()` が `新着メッセージ(3)` 等の
   子要素テキストを含めてしまう

**修正内容 (`webclass/crawler.py`):**
- `real_url = webclassurl + acspath` に変更（`/webclass/` 二重を除去）
- `NavigableString` で最初のテキストノードのみ取り出すよう変更
- `from bs4 import BeautifulSoup, NavigableString` に import 追加

**結果:** ✅ sections が正しく取得できることを確認（アルゴリズム・データ構造: 5 sections 等）

---

## 失敗記録

### TreePanel.svelte 展開不具合（Svelte リアクティビティ）
**原因:** `isOpen(key)` のような通常関数経由で `expandedKeys` を参照すると、
Svelte コンパイラがリアクティブ依存として追跡できない。
**対策:** テンプレート内で `expandedKeys.has(...)` を直接記述する。
