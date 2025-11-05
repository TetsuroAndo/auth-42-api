"""42認証モジュール

42のAPI認証とトークン管理を行うモジュールです。
再利用可能なモジュールとして設計されています。

主要なクラス:
    - Auth42: 認証クライアント
    - TokenManager: トークンの永続化管理
    - TokenInfo: トークン情報のデータクラス

例外クラス:
    - Auth42Error: 基底エラー
    - TokenError: トークン関連エラー
    - AuthenticationError: 認証失敗エラー
    - AuthorizationError: 認可失敗エラー
"""
from .exceptions import (
    Auth42Error,
    TokenError,
    AuthenticationError,
    AuthorizationError,
)
from .token import TokenInfo, TokenManager
from .client import Auth42

__all__ = [
    # 例外クラス
    "Auth42Error",
    "TokenError",
    "AuthenticationError",
    "AuthorizationError",
    # データクラス
    "TokenInfo",
    # 管理クラス
    "TokenManager",
    # 認証クライアント
    "Auth42",
]

__version__ = "0.1.0"
