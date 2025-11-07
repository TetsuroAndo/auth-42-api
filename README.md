# auth42 - 42 API認証ライブラリ

42 APIの認証とトークン管理を行う再利用可能なPythonライブラリです。
OAuth2クライアントクレデンシャルフローを使用して認証を行います。

## 特徴

- ✅ OAuth2準拠の認証フロー
- ✅ トークンの自動キャッシュと期限切れ前の自動更新
- ✅ 再利用可能なモジュール設計
- ✅ git submoduleとして利用可能
- ✅ 詳細なエラーハンドリング

## インストール

### git submoduleとして使用

```bash
# メインプロジェクトで
git submodule add <repository-url> src/auth42
git submodule update --init --recursive
```

### 依存関係のインストール

```bash
pip install requests
# または
uv add requests
```

## 使用方法

### 基本的な使用例

```python
from auth42 import Auth42, TokenManager

# 認証クライアントの作成
auth = Auth42(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# トークン取得（自動的にキャッシュ・更新）
token = auth.get_token()

# APIリクエスト用ヘッダー取得
headers = auth.get_headers()
```

### 環境変数からの設定読み込み

```python
import os
os.environ["FT_UID"] = "your_client_id"
os.environ["FT_SECRET"] = "your_client_secret"

# 環境変数から自動的に読み込まれる
auth = Auth42()
```

#### .envファイルの読み込みを無効にする

```python
# .envファイルを読み込まない
auth = Auth42(load_env=False)
```

サポートされている環境変数:
- `FT_UID`: 42 APIのクライアントID
- `FT_SECRET`: 42 APIのクライアントシークレット

### カスタムトークンマネージャーの使用

```python
from pathlib import Path
from auth42 import Auth42, TokenManager

# カスタムパスでトークンを保存
token_manager = TokenManager(token_file=Path("./custom_token.json"))
auth = Auth42(
    client_id="...",
    client_secret="...",
    token_manager=token_manager
)
```

### エラーハンドリング

```python
from auth42 import Auth42, TokenError, AuthenticationError, AuthorizationError

try:
    auth = Auth42(client_id="...", client_secret="...")
    token = auth.get_token()
except AuthenticationError as e:
    print(f"認証失敗: {e}")
except TokenError as e:
    print(f"トークンエラー: {e}")
```

### コマンドラインエントリーポイント

このライブラリはコマンドラインから直接実行可能なエントリーポイントを提供しています。

#### 基本的な使用方法

```bash
# 環境変数から認証情報を読み込む
export FT_UID=your_client_id
export FT_SECRET=your_client_secret
python -m auth42.main

# コマンドライン引数で認証情報を指定
python -m auth42.main --client-id your_client_id --client-secret your_client_secret

# トークン情報を取得して表示
python -m auth42.main --client-id your_client_id --client-secret your_client_secret --token-info

# 強制的に新しいトークンを取得
python -m auth42.main --client-id your_client_id --client-secret your_client_secret --force-refresh
```

#### オプション

- `--client-id`: 42 APIのクライアントID（環境変数 `FT_UID` からも取得可能）
- `--client-secret`: 42 APIのクライアントシークレット（環境変数 `FT_SECRET` からも取得可能）
- `--token-file`: トークンファイルのパス（環境変数 `TOKEN_FILE` からも取得可能）
- `--token-info`: トークン情報を取得して表示
- `--force-refresh`: 強制的に新しいトークンを取得

#### ヘルプの表示

```bash
python -m auth42.main --help
```

#### パッケージインストール後の使用

パッケージをインストールすると、`auth42`コマンドが直接使用可能になります：

```bash
# パッケージをインストール
pip install -e .

# コマンドラインから直接実行
auth42 --client-id your_client_id --client-secret your_client_secret --token-info
```

## APIリファレンス

### Auth42

認証クライアントクラス。

#### メソッド

- `get_token(force_refresh=False) -> str`: アクセストークンを取得
- `get_headers(force_refresh=False) -> Dict[str, str]`: APIリクエスト用ヘッダーを取得
- `get_token_info() -> Optional[Dict[str, Any]]`: トークン情報を取得
- `refresh_token() -> str`: トークンを強制的に更新

### TokenManager

トークンの永続化管理クラス。

#### メソッド

- `save_token(token_info: TokenInfo) -> None`: トークンを保存
- `load_token() -> Optional[TokenInfo]`: トークンを読み込み
- `clear_token() -> None`: トークンを削除
- `has_token() -> bool`: トークンファイルの存在確認

### TokenInfo

トークン情報を保持するデータクラス。

#### プロパティ

- `access_token: str`: アクセストークン
- `token_type: str`: トークンタイプ（通常は "bearer"）
- `expires_in: int`: 有効期限（秒）
- `created_at: float`: 作成時刻（Unixタイムスタンプ）
- `scope: Optional[str]`: スコープ

#### メソッド

- `is_expired: bool`: 期限切れかどうかを判定
- `expires_at: float`: 有効期限のUnixタイムスタンプ
- `to_dict() -> dict`: 辞書形式に変換
- `from_dict(data: dict) -> TokenInfo`: 辞書から作成（クラスメソッド）

## 例外クラス

- `Auth42Error`: 基底エラー
- `TokenError`: トークン関連エラー
- `AuthenticationError`: 認証失敗エラー（401）
- `AuthorizationError`: 認可失敗エラー（403）

## モジュール構造

```
auth42/
├── __init__.py          # パブリックAPIのエクスポート
├── exceptions.py        # 例外クラス
├── token.py            # TokenInfoとTokenManager
├── client.py           # Auth42認証クライアント
├── main.py             # コマンドラインエントリーポイント
├── pyproject.toml      # パッケージ設定
└── README.md           # このファイル
```

## ライセンス

このライブラリは再利用可能なモジュールとして設計されています。
