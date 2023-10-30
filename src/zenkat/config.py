from pathlib import Path
from copy import deepcopy
import tomllib
from zenkat.default_config import default_config

def adjust_config(original, adjuster):
    new_config = deepcopy(original)
    for key in adjuster:
        k = new_config.get(key)
        ak = adjuster.get(key)
        # need to see how this plays out with lists
        if type(k) == dict and type(ak) == dict:
            new_config[key] = adjust_config(new_config[key], adjuster[key])
            continue
        new_config[key] = adjuster[key]
    return new_config

def locate_themes() -> list[Path]:
    theme_paths = [(Path(__file__) / "../../../themes").resolve(), Path.home() / ".config/zenkat/themes"]
    themes = []
    
    for path in theme_paths:
        themes.extend(path.glob("*.toml"))

    return themes

def load_theme(path: Path):
    with open(path,"rb") as f:
        new_config = tomllib.load(f)
    return new_config

def load_config() -> dict:
    # load config from an escalating series of paths or default
    paths = [Path.home() / ".config/zenkat/config.toml"]
    # default settings
    config = default_config
    for path in paths:
        if not path.exists():
            continue
        with open(path, "rb") as f:
            new_config = tomllib.load(f)
        config = adjust_config(config, new_config)

    theme_preset = str(config.get("theme_preset"))
    if theme_preset is None: return config

    themes = locate_themes()

    for theme in themes:
        if theme.stem != theme_preset: continue
        try:
            config = adjust_config(config,load_theme(theme))
        except Exception:
            pass
        
    return config
