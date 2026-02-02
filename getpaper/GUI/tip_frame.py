import ttkbootstrap as ttk
from ttkbootstrap import Frame, Label, Progressbar, constants


class TipFrame(Frame):
    def __init__(self, master: ttk.Frame) -> None:
        super().__init__(master)
        self.columnconfigure(1, weight=1)
        self.label = Label(self, text="进度", width=16, anchor="e")
        self.label.grid(row=0, column=0, sticky=constants.E)
        self.bar = Progressbar(self, style="info.Striped.Horizontal.TProgressbar")
        self.bar.grid(row=0, column=1, sticky=constants.EW)

    def setTip(self, text: str) -> None:
        self.label["text"] = text
