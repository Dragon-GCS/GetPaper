import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tf


from getpaper.utils import getSpiderList, getSpider

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('GetPaper2.0')
        # 获取系统分辨率
        self.screenWidth = self.root.winfo_screenwidth()
        self.screenHeight = self.root.winfo_screenheight()
        # 限制窗口大小
        self.root.resizable(False, False)
        # 设置字体
        self.ft = tf.Font(family='微软雅黑', size=13)
        # 边距
        tk.Label(self.root, width=1, height=1).grid(row=0, column=0)
        tk.Label(self.root, width=1, height=0).grid(row=5, column=12)
        # 数据存储
        self.title_list = []
        self.author_list = []
        self.publication_list = []
        self.date_list = []
        self.abstract_list = []
        self.doi_list = []
        self.web_list = []
        # 表头
        self.columns = ('Title', 'Author', 'Data', 'Publication', 'Abstract', 'DOI', 'Web Address')

        # 第一行
        # 所查询的数据库
        tk.Label(self.root, text='查询数据库：', font=self.ft).grid(row=1, column=1, sticky='e')
        self.datebase = ttk.Combobox(self.root, values=['PubMed', 'ACS', 'DataBase3 is coming'], font=self.ft)
        self.datebase.grid(row=1, column=2, columnspan=5, sticky='w')
        self.datebase.current(0)

        # 第二行
        # 搜索提示
        tk.Label(self.root, text='请输入需要查找的关键词：', font=self.ft).grid(row=2, column=1, sticky='e')
        # 关键词
        self.keywd = tk.Entry(self.root, font=self.ft)
        self.keywd.grid(row=2, column=2, columnspan=7, sticky='we')
        self.keywd.focus()  # 程序运行时光标默认出现在窗口中
        # 搜索键
        search_button = tk.Button(self.root, text='Search', command=self.func, width=8, font=self.ft)
        search_button.grid(row=2, column=9, columnspan=2, sticky='w', padx=5)
        #search_button.bind('<Button-1>', self.func)

        # 第三行
        tk.Label(self.root, text='共查找到：', font=self.ft).grid(row=3, column=1, sticky='e')
        tk.Label(self.root, text='', font=self.ft).grid(row=3, column=2, sticky='ew')
        tk.Label(self.root, text='篇文献', font=self.ft).grid(row=3, column=3, sticky='w')
        tk.Label(self.root, text='请输入需要获取的文献数量：', font=self.ft).grid(row=3, column=7, sticky='e')
        # 输入文献数量
        self.num = tk.Entry(self.root, width=6, font=self.ft)
        self.num.grid(row=3, column=8)
        # 开始获取文献信息
        tk.Button(self.root, text='Get Them', command=self.func, width=8, font=self.ft) \
            .grid(row=3, column=9, columnspan=2, sticky='w', padx=5)

        # 创建表格
        self.excel = ttk.Treeview(self.root, show='headings', columns=self.columns,
                                  height=int((self.screenHeight - 10) * 52 / 1920))
        self.excel.grid(row=4, column=1, columnspan=9, sticky='we')
        # 设置表格宽度与文字居中
        self.excel.column('Title', width=int(self.screenWidth / 8), anchor='center')
        self.excel.column('Author', width=int(self.screenWidth / 10), anchor='center')
        self.excel.column('Data', width=int(self.screenWidth / 20), anchor='center')
        self.excel.column('Publication', width=int(self.screenWidth / 16), anchor='center')
        self.excel.column('Abstract', width=int(self.screenWidth / 6), anchor='center')
        self.excel.column('DOI', width=int(self.screenWidth / 16), anchor='center')
        self.excel.column('Web Address', width=int(self.screenWidth / 16), anchor='center')
        # 设置表头
        for i in self.columns:
            self.excel.heading(i, text=i)
        # 单击打开文献详情
        #self.excel.bind('<ButtonRelease-1>', self.open_abs)
        # 添加垂直滚动条
        vbar = ttk.Scrollbar(self.root, orient='vertical', command=self.func)
        self.excel.configure(yscrollcommand=vbar.set)
        vbar.grid(row=4, column=11, sticky='WNS')
        # 添加水平滚动条
        hbar = ttk.Scrollbar(self.root, orient='horizontal', command=self.func)
        self.excel.configure(xscrollcommand=hbar.set)
        hbar.grid(row=5, column=1, columnspan=10, sticky='NWE')

        # 保存、下载按钮
        menubar = tk.Menu(self.root)
        menubar.add_command(label='保存', command=self.func)
        menubar.add_command(label='下载', command=self.func)
        self.root['menu'] = menubar

    def run_it(self):
        self.root.mainloop()

    def func(self):
        pass