"""配置加载：合并 configs/*.toml 与 .env，环境变量优先。"""
import os
import tomllib
from pathlib import Path

# 项目根目录（src/ 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(env_path: Path) -> None:
    """轻量 .env 解析，避免额外依赖。"""
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(config_path: Path | None = None) -> dict:
    """读取 TOML 配置，敏感字段由 .env / 环境变量覆盖。"""
    config_path = config_path or (BASE_DIR / "configs" / "test.toml")
    _load_env_file(BASE_DIR / ".env")

    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    config = {
        **raw.get("base", {}),
        **raw.get("test_account", {}),
        "monitor": raw.get("monitor", {}),
    }

    # 环境变量优先（密钥等敏感信息放在 .env，不进入 git）
    if secret_key := os.getenv("SECRET_KEY"):
        config["secret_key"] = secret_key

    return config
