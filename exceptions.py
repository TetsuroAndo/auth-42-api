"""42認証モジュールの例外クラス

再利用可能なエラークラスを定義します。
"""
from typing import Optional


class Auth42Error(Exception):
    """42認証関連の基底エラー"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """エラーの初期化

        Args:
            message: エラーメッセージ
            status_code: HTTPステータスコード（オプション）
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TokenError(Auth42Error):
    """トークン取得・管理関連のエラー"""
    pass


class AuthenticationError(Auth42Error):
    """認証失敗エラー"""
    pass


class AuthorizationError(Auth42Error):
    """認可失敗エラー（権限不足）"""
    pass
