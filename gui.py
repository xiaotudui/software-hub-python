from tkinter import *
from tkinter import ttk
from system.SysInfo import getSysInfo

def getList():
    sysInfo = getSysInfo()
    print(sysInfo)


window = Tk()

window.title('PS下载安装程序')

window.geometry('500x300')

bt_get_list = ttk.Button(window, text='检测', command=getList)
bt_onceclick = ttk.Button(window, text='一键安装')

bt_onceclick.pack()
bt_get_list.pack()
window.mainloop()
