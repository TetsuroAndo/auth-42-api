"""42 API認証クライアントのエントリーポイント

コマンドライン引数や環境変数からクライアントIDとシークレットを受け取り、
42 API認証をテストします。
"""
import argparse
import sys

from .client import Auth42
from .token import TokenManager


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="42 API認証クライアントのエントリーポイント",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数から認証情報を読み込む（トークンのみをstdoutに出力）
  export FT_UID=your_client_id
  export FT_SECRET=your_client_secret
  python -m auth42.main

  # コマンドライン引数で認証情報を指定
  python -m auth42.main --client-id your_client_id --client-secret your_client_secret

  # トークン情報を取得（stderrに表示）
  python -m auth42.main --token-info

  # パイプでトークンを取得して使用
  TOKEN=$(python -m auth42.main 2>/dev/null)
        """.strip()
    )

    parser.add_argument(
        "--client-id",
        type=str,
        default=None,
        help="42 APIのクライアントID（環境変数 FT_UID からも取得可能）",
    )
    parser.add_argument(
        "--client-secret",
        type=str,
        default=None,
        help="42 APIのクライアントシークレット（環境変数 FT_SECRET からも取得可能）",
    )
    parser.add_argument(
        "--token-file",
        type=str,
        default=None,
        help="トークンファイルのパス（環境変数 TOKEN_FILE からも取得可能）",
    )
    parser.add_argument(
        "--token-info",
        action="store_true",
        help="トークン情報を取得して表示",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="強制的に新しいトークンを取得",
    )

    args = parser.parse_args()

    try:
        # トークンマネージャーを初期化
        token_manager = TokenManager(token_file=args.token_file)

        # 認証クライアントを初期化
        auth = Auth42(
            client_id=args.client_id,
            client_secret=args.client_secret,
            token_manager=token_manager,
        )

        # 情報メッセージはstderrに出力（stdoutを汚さないため）
        print("✅ 42認証クライアントの初期化に成功しました", file=sys.stderr)
        print(f"   Base URL: {auth.base_url}", file=sys.stderr)

        # トークンを取得
        print("\n🔑 アクセストークンを取得中...", file=sys.stderr)
        try:
            token = auth.get_token(force_refresh=args.force_refresh)
            print("✅ アクセストークンの取得に成功しました", file=sys.stderr)

            # トークンだけをstdoutに出力（パイプで使用可能）
            print(token, file=sys.stdout)

            # トークン情報を取得
            if args.token_info:
                print("\n📋 トークン情報を取得中...", file=sys.stderr)
                token_info = auth.get_token_info()
                if token_info:
                    print("✅ トークン情報の取得に成功しました", file=sys.stderr)
                    for key, value in token_info.items():
                        print(f"   {key}: {value}", file=sys.stderr)
                else:
                    print("⚠️  トークン情報の取得に失敗しました", file=sys.stderr)

        except Exception as e:
            print(f"❌ トークンの取得に失敗しました: {e}", file=sys.stderr)
            sys.exit(1)

    except ValueError as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
