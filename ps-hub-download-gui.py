import json
import platform
from tkinter import *

# 主窗口
from tkinter import ttk

import requests


# 用获取到的所有软件清单，输出适合操作系统的列表
def infos2list(jsonInfo):
    downlist = []
    # ----------------------------
    # sys_name in ['mac', 'win']
    # sys_bit in ['64bit', '32bit']
    # ----------------------------
    global sys_name
    global sys_bit
    for key, value in jsonInfo.items():
        if sys_name in value['requirements'] and sys_bit in value['requirements']:
            if 'recommend' in value['requirements']:
                downlist.insert(0, key + '【推荐】')
            else:
                downlist.append(key)
    return downlist


# 获得版本中的大版本数字
def getFirstNum(strnum):
    res = ""
    for i in strnum:
        if i.isdigit():
            res += i
        else:
            break
    return res


# 获取用户选中的内容
def getUserChoose():
    global listbox
    # print('click me')
    # print(listbox.get().split('【')[0])
    return listbox.get().split('【')[0]


# 挑选适合计算机的版本
def all2suit(jsonInfo):
    suit_list = []
    global sys_name
    global sys_bit
    sys_version = platform.version()
    sys_version = getFirstNum(sys_version)

    for key, value in jsonInfo.items():
        if sys_bit in value['requirements'] and sys_name+sys_version in value['requirements']:
            if 'recommend' in value['requirements']:
                suit_list.insert(0, key+'【推荐】')
            else:
                suit_list.append(key)
    return suit_list

# 获得下载链接
def parseDownloadLink(SHARE_URL, REQUEST_URL, user_agent, cookie, host):
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie,
        'Host': host,
        'Referer': SHARE_URL
    }
    data = requests.post(REQUEST_URL, headers=headers)
    # print(data.content)
    return json.loads(data.content)



# 下载选中的软件
def startDown():
    target_down = getUserChoose()
    global sys_soft_list
    request_url = sys_soft_list[target_down]['DownLink']
    user_agent = sys_soft_list[target_down]['User-Agent']
    share_url = sys_soft_list[target_down]['Referer']
    



# ----------------main------------------
root = Tk()
root.title('PS/PhotoShop一键安装程序')
width = 500
heigth = 400
root.geometry('{}x{}'.format(width, heigth))

# 获取系统参数
sys_bit = platform.architecture()[0]
sys_name = platform.system()
if sys_name == 'Darwin':
    sys_name = 'mac'
else:
    sys_name = 'win'

# 选择与系统匹配的API地址
APIs = {'win': 'http://tuduia.gitee.io/software-hub-api/win-ps.json',
        'mac': 'http://tuduia.gitee.io/software-hub-api/mac-ps.json'}
APIURL = None
if sys_name == 'win':
    API_URL = APIs['win']
else:
    API_URL = APIs['mac']

# 启动时候，尝试获得一次软件清单
sys_soft_list = None
data = None
try:
    data = requests.get(API_URL)
except:
    pass

if data != None and data.status_code == 200:
    sys_soft_list = json.loads(data.content)

# 如果启动时候获取失败，添加按钮让用户重新获取
soft_list_frame = Frame(root)
soft_list_frame.pack()
text_startup = StringVar()

get_list_btn = ttk.Button(soft_list_frame, text='重新获取')
listbox = ttk.Combobox(soft_list_frame)
label_startup = ttk.Label(soft_list_frame, textvariable=text_startup)

if sys_soft_list == None:
    text_startup.set('请检查网络连接，点击下方按钮重新获取')
    listbox.set('请点击按钮重新获取')
    label_startup.grid(row=0)
    listbox.grid(row=1, column=0)
    get_list_btn.grid(row=1, column=1)
else:
    text_startup.set('已成功获取您电脑可以运行的版本，请选择')
    label_startup.grid(row=0)
    listbox['value'] = all2suit(sys_soft_list)
    listbox.set(all2suit(sys_soft_list)[0])
    listbox.grid(row=1, column=0)


# 设置下载界面
down_frame = Frame(root)
down_frame.pack()
btn_down = ttk.Button(down_frame, text='下载', command=getUserChoose)
btn_pause = ttk.Button(down_frame, text='暂停')
label_down = ttk.Label(down_frame, text='下载进度')
bar_down = ttk.Progressbar(down_frame, length=100)
var_down = StringVar(down_frame)
var_down.set('0 KB/s')
label_speed = ttk.Label(down_frame, textvariable=var_down)

btn_down.grid(row=0, column=0)
btn_pause.grid(row=0, column=1)
label_down.grid(row=1, column=0)
bar_down.grid(row=1, column=1)
label_speed.grid(row=1, column=2)


# 设置安装界面
install_frame = Frame(root)
install_frame.pack()
btn_install = ttk.Button(install_frame, text='安装')
btn_install.grid(row=0)

root.mainloop()
