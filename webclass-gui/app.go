package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

// App struct
type App struct {
	ctx     context.Context
	python  string
	cliPath string
}

// --- ツリー構造の型定義（Python cli.py の出力と対応）---

type Item struct {
	Chapter string `json:"chapter"`
	Query   string `json:"query"`
}

type Content struct {
	ID            string `json:"id,omitempty"`
	Name          string `json:"name"`
	Type          string `json:"type"`
	Items         []Item `json:"items,omitempty"`
	DownloadQuery string `json:"download_query,omitempty"`
	URL           string `json:"url,omitempty"`
	Reason        string `json:"reason,omitempty"`
}

type Section struct {
	Name     string    `json:"name"`
	Contents []Content `json:"contents"`
}

type Course struct {
	Slot     string    `json:"slot"`
	Name     string    `json:"name"`
	URL      string    `json:"url"`
	Sections []Section `json:"sections"`
	Error    string    `json:"error,omitempty"`
}

type Tree struct {
	Courses []Course `json:"courses"`
}

// ---

func NewApp() *App {
	return &App{}
}

func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	a.resolvePaths()
}

// resolvePaths は Python 実行ファイルと cli.py のパスを解決する。
// wails dev では cwd が webclass-gui/ になるため、プロジェクトルートは ../
func (a *App) resolvePaths() {
	cwd, _ := os.Getwd()
	projectRoot := filepath.Join(cwd, "..")

	venvPython := filepath.Join(projectRoot, ".venv", "bin", "python3")
	if _, err := os.Stat(venvPython); err == nil {
		a.python = venvPython
	} else {
		a.python = "python3"
	}

	a.cliPath = filepath.Join(projectRoot, "webclass", "cli.py")
}

func (a *App) runCLI(args ...string) ([]byte, error) {
	cmdArgs := append([]string{a.cliPath}, args...)
	cmd := exec.Command(a.python, cmdArgs...)
	cmd.Dir = filepath.Dir(a.cliPath)
	out, err := cmd.Output()
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			return nil, fmt.Errorf("%w\nstderr: %s", err, string(exitErr.Stderr))
		}
		return nil, err
	}
	return out, nil
}

// CheckCredentials は認証情報が保存済みかどうかを返す
func (a *App) CheckCredentials() bool {
	cmd := exec.Command(a.python, a.cliPath, "check-credentials")
	cmd.Dir = filepath.Dir(a.cliPath)
	return cmd.Run() == nil
}

// SetCredentials はユーザーIDとパスワードを暗号化保存する
func (a *App) SetCredentials(userid, password string) error {
	_, err := a.runCLI("set-credentials", "--userid", userid, "--password", password)
	return err
}

// GetTree はコース構造ツリーを返す（クロールに数分かかる場合あり）
func (a *App) GetTree() (*Tree, error) {
	out, err := a.runCLI("tree")
	if err != nil {
		return nil, fmt.Errorf("tree 取得エラー: %w", err)
	}
	var tree Tree
	if err := json.Unmarshal(out, &tree); err != nil {
		return nil, fmt.Errorf("JSON パースエラー: %w\n出力: %.200s", err, string(out))
	}
	return &tree, nil
}

// DownloadPDF は指定クエリの PDF をローカルに保存する
func (a *App) DownloadPDF(query, savePath string) error {
	_, err := a.runCLI("download", "--query", query, "--path", savePath)
	return err
}

// GetCacheDir は PDF キャッシュディレクトリのパスを返す
func (a *App) GetCacheDir() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".webclass-gui", "cache")
}

// FetchPDF はクエリの PDF をバイト列で返す。
// キャッシュ (GetCacheDir/<sha256(query)>.pdf) があればそれを返し、
// なければ Python CLI でダウンロードしてキャッシュに保存する。
func (a *App) FetchPDF(query string) ([]byte, error) {
	cacheDir := a.GetCacheDir()
	if err := os.MkdirAll(cacheDir, 0o755); err != nil {
		return nil, err
	}

	sum := sha256.Sum256([]byte(query))
	cachePath := filepath.Join(cacheDir, hex.EncodeToString(sum[:])+".pdf")

	// キャッシュヒット
	if data, err := os.ReadFile(cachePath); err == nil && len(data) >= 4 && string(data[:4]) == "%PDF" {
		return data, nil
	}

	if _, err := a.runCLI("download", "--query", query, "--path", cachePath); err != nil {
		return nil, err
	}
	return os.ReadFile(cachePath)
}

// ClearPDFCache はキャッシュ済みPDFを全削除する
func (a *App) ClearPDFCache() error {
	return os.RemoveAll(a.GetCacheDir())
}
