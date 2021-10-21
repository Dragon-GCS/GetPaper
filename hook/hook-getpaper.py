from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.joinpath("getpaper")

def getlist(dir):
    names = [module.name.rstrip(".py") for module in ROOT_DIR.glob(dir + "/*.py") if not module.name.startswith("_")]
    return [f"getpaper.{dir}.{name}" for name in names]
spiders = getlist("spiders")
translators = getlist("translator")

hiddenimports = [*spiders, *translators]
