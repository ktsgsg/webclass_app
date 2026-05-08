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
**目的:** `main.py` を CLI として整備し、`--output json` で構造ツリーを stdout 出力できるようにする

**実施内容:**
- [ ] `main.py` に argparse 追加（`--output json` / `--download <id>`）
- [ ] `build_tree()` の結果を stdout に JSON 出力
- [ ] PDF ダウンロードをコマンドライン引数で指定可能に
- [ ] メッセージ一覧取得の CLI 対応

**結果:** 未着手

---

### [Phase 2] Wails プロジェクト初期化
**ブランチ:** `feature/wails-init`
**目的:** Wails + Svelte のデスクトップアプリ雛形を作成

**実施内容:**
- [ ] `wails init -n webclass-gui -t svelte`
- [ ] Go バインディング: Python subprocess 呼び出し
- [ ] JSON パースして Svelte に渡す構造定義

**結果:** 未着手

---

### [Phase 3] 左ペインツリーUI
**ブランチ:** `feature/tree-ui`
**目的:** 時間割→科目→教材の3階層ツリーを左ペインに表示

**実施内容:**
- [ ] Svelte ツリーコンポーネント実装
- [ ] 展開/折りたたみ
- [ ] 締切バッジ・新着メッセージバッジ

**結果:** 未着手

---

### [Phase 4] 右ペインコンテンツ表示
**ブランチ:** `feature/content-view`
**目的:** 選択ノードに応じて PDF ビューワー / メッセージ一覧を表示

**実施内容:**
- [ ] PDF インライン表示（Wails の webview 活用）
- [ ] メッセージ一覧・詳細表示
- [ ] 課題提出フォーム（PDF アップロード）

**結果:** 未着手

---

## 既知の課題・注意事項
- WebClass の JS リダイレクト（偽リダイレクト）は `getacs()` で処理済み
- 課題提出は multipart POST（詳細調査が必要）
- 認証情報は `key.key` / `userdata.txt` に保存（.gitignore 済み）
- `structure.json` も .gitignore 済み

## 失敗記録
_失敗した実装はここに記録する_
