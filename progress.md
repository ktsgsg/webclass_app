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

## 失敗記録
_失敗した実装はここに記録する_
