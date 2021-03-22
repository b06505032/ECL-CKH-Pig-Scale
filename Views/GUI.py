from Views.StartView import *
from Views.ScaleView import *
from Views.AnalyzeView import *

class GUI(tk.Tk):
    def __init__(self, system, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.Frame = StartView(parent=self.container, controller=self, system=system)
        self.Frame.grid(row=0, column=0, sticky="nsew")


    def show_frame(self, page_name, system):
        self.Frame.destroy()
        f = Frame()
        if page_name == "StartView":
            f = StartView(parent=self.container, controller=self, system=system)
        elif page_name == "ScaleView":
            f = ScaleView(parent=self.container, controller=self, system=system)
        elif page_name == "AnalyzeView":
            f = AnalyzeView(parent=self.container, controller=self, system=system)
        f.grid(row=0, column=0, sticky="nsew")
        self.Frame = f
        
