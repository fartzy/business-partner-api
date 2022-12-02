import pathlib
import tomllib as toml

_TOML = toml.load(
    open(str(pathlib.Path(__file__).parent.resolve() / "config.toml"), "rb")
)

DB_CONFIGS = _TOML["db"]
APP_NAME = _TOML["app"]["name"]
APP_VERSION = _TOML["app"]["version"]
