"""42 API認証クライアント

OAuth2クライアントクレデンシャルフローを使用して42 APIの認証を行います。
"""
import os
import json
import time
from typing import Optional, Dict, Any
import requests

from .exceptions import TokenError, AuthenticationError, AuthorizationError
from .token import TokenInfo, TokenManager


class Auth42:
    """42 API認証クラス

    OAuth2クライアントクレデンシャルフローを使用して認証を行い、
    トークンの取得と管理を行います。
    """

    BASE_URL = "https://api.intra.42.fr"
    TOKEN_ENDPOINT = "/oauth/token"
    TOKEN_INFO_ENDPOINT = "/oauth/token/info"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_manager: Optional[TokenManager] = None,
        base_url: Optional[str] = None,
    ):
        """42認証クラスの初期化

        Args:
            client_id: 42 APIのクライアントID（環境変数からも取得可能）
            client_secret: 42 APIのクライアントシークレット（環境変数からも取得可能）
            token_manager: トークンマネージャー（デフォルト: TokenManager()）
            base_url: APIのベースURL（デフォルト: https://api.intra.42.fr）
        """
        self.base_url = base_url or self.BASE_URL
        self.token_manager = token_manager or TokenManager()

        # 環境変数から取得
        self.client_id = client_id or os.getenv("FT_UID")
        self.client_secret = client_secret or os.getenv("FT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "client_id と client_secret が必要です。\n"
                "環境変数を以下のように設定してください:\n"
                "- FT_UID: 42 APIのクライアントID\n"
                "- FT_SECRET: 42 APIのクライアントシークレット"
            )

    def get_token(self, force_refresh: bool = False) -> str:
        """有効なアクセストークンを取得

        Args:
            force_refresh: 強制的に新しいトークンを取得するか

        Returns:
            アクセストークン文字列

        Raises:
            TokenError: トークン取得に失敗した場合
        """
        # 保存されたトークンを確認
        if not force_refresh:
            token_info = self.token_manager.load_token()
            if token_info and not token_info.is_expired:
                return token_info.access_token

        # 新しいトークンを取得
        token_info = self._request_token()
        self.token_manager.save_token(token_info)
        return token_info.access_token

    def _request_token(self) -> TokenInfo:
        """OAuth2クライアントクレデンシャルフローでトークンを取得

        Returns:
            TokenInfo: 取得したトークン情報

        Raises:
            TokenError: トークン取得に失敗した場合
        """
        url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
        # x-www-form-urlencoded形式で送信（data引数を使用）
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            # HTTPS必須（requestsはデフォルトでHTTPSを使用）
            response = requests.post(url, data=data)

            # エラーハンドリング
            if response.status_code == 400:
                raise TokenError(
                    f"リクエストの形式が不正です: {response.text}\n"
                    "client_id と client_secret が正しいか確認してください。",
                    status_code=400
                )
            elif response.status_code == 401:
                raise AuthenticationError(
                    f"認証に失敗しました: {response.text}\n"
                    "client_id と client_secret が正しいか確認してください。",
                    status_code=401
                )
            elif response.status_code == 403:
                raise AuthorizationError(
                    f"アクセスが拒否されました: {response.text}\n"
                    "アプリケーションの権限を確認してください。",
                    status_code=403
                )
            elif not response.ok:
                raise TokenError(
                    f"トークン取得に失敗しました (HTTP {response.status_code}): {response.text}",
                    status_code=response.status_code
                )

            token_data = response.json()

            # 必須フィールドの確認
            if "access_token" not in token_data:
                raise TokenError("レスポンスに access_token が含まれていません")

            return TokenInfo(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "bearer"),
                expires_in=token_data.get("expires_in", 7200),  # デフォルト2時間
                created_at=time.time(),
                scope=token_data.get("scope"),
            )
        except requests.exceptions.ConnectionError as e:
            raise TokenError(
                f"APIへの接続に失敗しました: {e}\n"
                "HTTPSを使用しているか確認してください。"
            ) from e
        except requests.exceptions.RequestException as e:
            raise TokenError(f"リクエスト中にエラーが発生しました: {e}") from e
        except json.JSONDecodeError as e:
            raise TokenError(f"レスポンスのJSON解析に失敗しました: {e}") from e

    def get_headers(self, force_refresh: bool = False) -> Dict[str, str]:
        """APIリクエスト用のヘッダーを取得

        Args:
            force_refresh: 強制的に新しいトークンを取得するか

        Returns:
            認証ヘッダーを含む辞書

        Raises:
            TokenError: トークン取得に失敗した場合
        """
        token = self.get_token(force_refresh=force_refresh)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """トークン情報を取得（/oauth/token/infoエンドポイントを使用）

        Returns:
            トークン情報の辞書（取得に失敗した場合はNone）
        """
        try:
            url = f"{self.base_url}{self.TOKEN_INFO_ENDPOINT}"
            headers = self.get_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 401:
                # トークンが無効な場合は再取得を試みる
                headers = self.get_headers(force_refresh=True)
                response = requests.get(url, headers=headers)

            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def refresh_token(self) -> str:
        """トークンを強制的に更新

        Returns:
            新しいアクセストークン文字列

        Raises:
            TokenError: トークン取得に失敗した場合
        """
        return self.get_token(force_refresh=True)
