from getpaper.config import spider_list, translator_list

hiddenimports = [f"getpaper.spiders.{module}" for module in spider_list] + \
                [f"getpaper.translator.{module}" for module in translator_list]
