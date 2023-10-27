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

def load_config() -> dict:
    # load config from an escalating series of paths or default
    paths = [Path.home() / ".config/zenkat/config.toml"]
    theme_path = (Path(__file__) / "../../../themes").resolve()
    # default settings
    config = default_config
    for path in paths:
        if not path.exists():
            continue
        with open(path, "rb") as f:
            new_config = tomllib.load(f)
        config = adjust_config(config, new_config)

        theme_preset = str(config.get("theme_preset"))
        if theme_preset is None: continue

        with open(theme_path / theme_preset,"rb") as f:
            new_config = tomllib.load(f)
        config = adjust_config(config,new_config)
            
    return config
