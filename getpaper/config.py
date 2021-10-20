from pathlib import Path
import sys

ROOT_DIR = Path(sys.executable 
                if hasattr(sys, "frozen") 
                else __file__).parent

HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/80.0.3987.132 Safari/537.36'}

TIMEOUT = 15

APP_NAME = "GetPaper"
