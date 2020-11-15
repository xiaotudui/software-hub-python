import datetime
import os
import tempfile
from tkinter import *
from tkinter import simpledialog, ttk


def genPassword():
    seed1 = datetime.datetime.now().isocalendar()
    seed2 = 123
    res = seed1[0]*123+seed1[1]*123
    res = str(res)
    return res[:4]


def valid():
    file_validate = os.path.join(tempfile.gettempdir(), 'ps-license')
    if os.path.exists(file_validate):
        return True
    else:
        input = simpledialog.askstring(title='注册', prompt='请输入验证码')
        if str(input) == str(genPassword()):
            with open(file_validate, 'w') as f:
                f.write('ok')
            return True
        else:
            return False

root = Tk()
root.geometry('500x400')
valid()
root.mainloop()
