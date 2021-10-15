from pathlib import Path
import sys

ROOT_DIR = Path(sys.executable 
                if hasattr(sys, "frozen") 
                else __file__).parent
