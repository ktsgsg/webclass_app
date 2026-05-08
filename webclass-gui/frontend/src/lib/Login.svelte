<script>
  import { SetCredentials } from '../../wailsjs/go/main/App.js'

  export let onSuccess

  let userid = ''
  let password = ''
  let loading = false
  let error = ''

  async function handleSubmit() {
    if (!userid || !password) {
      error = 'ユーザーIDとパスワードを入力してください'
      return
    }
    loading = true
    error = ''
    try {
      await SetCredentials(userid, password)
      onSuccess()
    } catch (e) {
      error = '認証情報の保存に失敗しました: ' + e
    } finally {
      loading = false
    }
  }
</script>

<div class="login-overlay">
  <div class="login-card">
    <h1>WebClass</h1>
    <p class="subtitle">名城大学統合ポータル (meijo SSO) のID・パスワードを入力してください</p>
    <form on:submit|preventDefault={handleSubmit}>
      <label>
        ユーザーID
        <input
          type="text"
          bind:value={userid}
          placeholder="学籍番号など"
          autocomplete="username"
          disabled={loading}
        />
      </label>
      <label>
        パスワード
        <input
          type="password"
          bind:value={password}
          placeholder="パスワード"
          autocomplete="current-password"
          disabled={loading}
        />
      </label>
      {#if error}
        <p class="error">{error}</p>
      {/if}
      <button type="submit" disabled={loading}>
        {loading ? '保存中...' : 'ログイン'}
      </button>
    </form>
    <p class="note">認証情報はローカルに暗号化して保存されます。次回から入力不要です。</p>
  </div>
</div>

<style>
  .login-overlay {
    position: fixed;
    inset: 0;
    background: #1a1a2e;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .login-card {
    background: #16213e;
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 2.5rem;
    width: 380px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  }

  h1 {
    margin: 0 0 0.25rem;
    font-size: 1.8rem;
    color: #e94560;
    font-weight: 700;
  }

  .subtitle {
    margin: 0 0 1.5rem;
    font-size: 0.8rem;
    color: #8892a4;
    line-height: 1.5;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    font-size: 0.85rem;
    color: #a8b2c1;
  }

  input {
    padding: 0.6rem 0.8rem;
    border: 1px solid #0f3460;
    border-radius: 6px;
    background: #0f3460;
    color: #e2e8f0;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
  }

  input:focus {
    border-color: #e94560;
  }

  input:disabled {
    opacity: 0.5;
  }

  button {
    margin-top: 0.5rem;
    padding: 0.7rem;
    background: #e94560;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  button:hover:not(:disabled) {
    background: #c73652;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .error {
    color: #e94560;
    font-size: 0.82rem;
    margin: 0;
  }

  .note {
    margin: 1.2rem 0 0;
    font-size: 0.75rem;
    color: #5a6478;
    text-align: center;
  }
</style>
