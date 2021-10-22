from getpaper.GUI import Application
from multiprocessing import freeze_support
import getpaper # for pyinstall

if __name__ == '__main__':
    freeze_support()    # 防止打包后多进程导致的重复开启窗口
    app = Application("flatly")
    app.run()

