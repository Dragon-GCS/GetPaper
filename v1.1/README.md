## 功能
* 根据输入的关键词，从选择的数据库中爬取文献的标题、作者、期刊、日期、摘要、doi和网址等信息。

* 保存按钮可以将爬取到的信息保存至本地。

* 下载按钮是根据爬取到的doi信息从sci-hub下载文献，但有时会出现http.client.IncompleteRead导致文献无法下载，与个人网络情况有关。

## 后续改进计划
* 优化爬取结果的表现方法

* 可从结果中选择需要下载的文献

* 尝试增加其他数据库

* 使用多线程提高文献信息获取速度

## 下载地址
* pyinstaller打包后的exe文件大小为27M，所以保存到网盘里了。

* 链接：https://pan.baidu.com/s/1NOjpPXyvy3kmJOIpUHXoHg 
提取码：0u7n

## 其他
软件的目的是通过一个软件可以爬取各个数据库的文献信息，但是大部分数据库都需要版权，出了学校就上不去了，所以目前只做了PubMed和ACS两个库。

目前由于要依次访问文献的网址，耗时会比较久，而且不稳定，成功率也不到，后面考虑用多线程提高一下速度。

这是我自己学习Python后自己做的第一个程序，不知道效果如何，后续有时间的话会继续改进。
