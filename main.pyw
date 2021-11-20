import logging
logging.basicConfig(level=logging.INFO,
                    datefmt = "%H:%M:%S",
                    format = "[%(asctime)s %(levelname)s] - %(filename)s[line:%(lineno)d] - Thread[%(threadName)s]\n%(message)s")

from getpaper.GUI import Application

if __name__ == "__main__":
    app = Application("flatly")
    app.run()
