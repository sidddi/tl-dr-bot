import os

# Set required env vars before any project module is imported
os.environ.setdefault("TELEGRAM_TOKEN", "test-telegram-token")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("GITHUB_TOKEN", "test-github-token")
os.environ.setdefault("GITHUB_VAULT_REPO", "test-user/test-vault")
os.environ.setdefault("GITHUB_VAULT_BASE_PATH", "TL-DR")
