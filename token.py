"""42認証トークン管理モジュール

トークン情報のデータクラスとトークンの永続化管理を提供します。
"""
import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class TokenInfo:
    """トークン情報を保持するデータクラス"""
    access_token: str
    token_type: str
    expires_in: int
    created_at: float
    scope: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """トークンが期限切れかどうかを判定

        Returns:
            期限切れの場合True、有効な場合False
        """
        elapsed = time.time() - self.created_at
        return elapsed >= (self.expires_in - 60)  # 1分のマージンを持たせる

    @property
    def expires_at(self) -> float:
        """トークンの有効期限を取得

        Returns:
            有効期限のUnixタイムスタンプ
        """
        return self.created_at + self.expires_in

    def to_dict(self) -> dict:
        """辞書形式に変換

        Returns:
            トークン情報の辞書
        """
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "created_at": self.created_at,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenInfo":
        """辞書からTokenInfoオブジェクトを作成

        Args:
            data: トークン情報の辞書

        Returns:
            TokenInfoオブジェクト
        """
        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in", 7200),
            created_at=data.get("created_at", time.time()),
            scope=data.get("scope"),
        )


class TokenManager:
    """トークンの保存と読み込みを管理するクラス"""

    def __init__(self, token_file: Optional[Path] = None):
        """トークンマネージャーの初期化

        Args:
            token_file: トークンを保存するファイルパス（デフォルト: ~/.42_token.json）
        """
        if token_file is None:
            token_file = Path.home() / ".42_token.json"
        self.token_file = Path(token_file)

    def save_token(self, token_info: TokenInfo) -> None:
        """トークンをファイルに保存

        Args:
            token_info: 保存するトークン情報
        """
        data = token_info.to_dict()
        with open(self.token_file, "w") as f:
            json.dump(data, f)

    def load_token(self) -> Optional[TokenInfo]:
        """保存されたトークンを読み込む

        Returns:
            トークン情報（ファイルが存在しない、または読み込みに失敗した場合はNone）
        """
        if not self.token_file.exists():
            return None

        try:
            with open(self.token_file, "r") as f:
                data = json.load(f)
            return TokenInfo.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def clear_token(self) -> None:
        """保存されたトークンを削除"""
        if self.token_file.exists():
            self.token_file.unlink()

    def has_token(self) -> bool:
        """トークンファイルが存在するか確認

        Returns:
            ファイルが存在する場合True
        """
        return self.token_file.exists()
