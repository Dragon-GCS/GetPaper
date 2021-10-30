

## GetPaper 2.0 -- 2021.11

python3.8+
开发中。。。

* 使用ttk.bootstrap重新设计GUI，增加作者、期刊、日期、排序方式选项
* 调整项目结构，增加爬虫接口，方便后期添加新的爬虫引擎
* 使用多线程和协程提高爬取效率同时解决搜索时的线程阻塞问题
* 增加翻译功能接口，可自行添加不同的翻译源，自带百度翻译，需填写AppId

项目结构
```bash
├─getpaper
│  ├─GUI            # GUi模块
│  ├─spiders        # 爬虫模块
│  ├─translator     # 翻译模块
│  ├─config.py      # 相关配置文件
│  ├─download.py    # Sci-Hub下载模块
│  └─utils.py       # 工具模块
├─hook              # 用于pyinstaller打包，用于导入项目中动态导入的模块
└─main.py           # 入口
```
### 爬虫引擎与翻译引擎接口
在相应的模块内添加`name.py`文件，并在`config.py`中添加对应的`<name>`

* 爬虫
  * 类名必须为`Spider`
  * `getTotalnum()`根据查找信息获取搜索结果总数
  * `getAllpapers(num: int)` 获取指定数量的文章详情
  * `utils`中的`TipException`用于捕获任务中的异常并在GUI上显示`tip`信息,不超过16个字符`raise TipException(tip)` 
  * `restul_queue`为一个`PriorityQueue`对象，用于保存结果，`restul_queue.qsize()`用于监控进度，爬虫中引发异常时应填满队列，否则在TIMEOUT前下载按钮将不可用。
* 翻译
  * 类名必须为`Translator`
  * 实现`translate(self, detail: str) -> str`，文章title和abstract会分别调用此方法进行翻译，返回的字符串会通过`str()`显示到文本框内。

---

## GetPaper 1.0
* 根据输入的关键词，从选择的数据库中爬取文献的标题、作者、期刊、日期、摘要、doi和网址等信息。

* 保存按钮可以将爬取到的信息保存至本地。

* 下载按钮是根据爬取到的doi信息从sci-hub下载文献，但有时会出现http.client.IncompleteRead导致文献无法下载，与个人网络情况有关。

## 后续改进计划

* 优化爬取结果的表现方法

* 可从结果中选择需要下载的文献

* 尝试增加其他数据库

* 使用多线程提高文献信息获取速度

## 下载地址
* pyinstaller打包后的exe文件大小为27M，保存在百度网盘[提取码：0u7n](https://pan.baidu.com/s/1NOjpPXyvy3kmJOIpUHXoHg)。

