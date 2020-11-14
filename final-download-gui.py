import json
import os
import platform
import tempfile
import threading
import time
from tkinter import *
import tkinter.messagebox

# 主窗口
from tkinter import ttk
from urllib.parse import unquote

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
        if sys_bit in value['requirements'] and sys_name + sys_version in value['requirements']:
            if 'recommend' in value['requirements']:
                suit_list.insert(0, key + '【推荐】')
            else:
                suit_list.append(key)
    return suit_list


# 获得下载链接
def parseDownloadLink(SHARE_URL, REQUEST_URL, user_agent, cookie, host):
    global root
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie,
        'Host': host,
        'Referer': SHARE_URL
    }
    data = None
    try:
        data = requests.post(REQUEST_URL, headers=headers)
    except:
        pass
    return data


# 下载

def download(url, file_folder, temp_name):
    global var_down
    global bar_down
    global label_speed
    global root
    file_name = temp_name
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])

    headers = r1.headers
    #
    if 'Content-Disposition' in headers and headers['Content-Disposition']:
        disposition_split = headers['Content-Disposition'].split(';')
        if len(disposition_split) > 1:
            if disposition_split[1].strip().lower().startswith('filename='):
                file_name = disposition_split[1].split('=')
                if len(file_name) > 1:
                    file_name = unquote(file_name[1])

    file_path = os.path.join(file_folder, file_name)
    # 这重要了，先看看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    # 显示一下下载了多少
    print(temp_size)
    print(total_size)
    # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers)

    # 下面写入文件也要注意，看到"ab"了吗？
    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024 * 8):
            startTime = time.time()
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                bar_down['value'] = 100 * temp_size / total_size
                var_down.set(str(int(len(chunk) / 1024 / 1024 / (time.time() - startTime))))
                # var_down.set("\r[%s%s] %d%% %dKB/S" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size,
                #                                            int(len(chunk) / 1024 / 1024 / (time.time() - startTime))))
                sys.stdout.write("\r[%s%s] %d%% %dKB/S" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size,
                                                           int(len(chunk) / 1024 / 1024 / (time.time() - startTime))))
                sys.stdout.flush()
                # root.update_idletasks()
    print()  # 避免上面\r 回车符


# 下载选中的软件
def startDown():
    target_down = getUserChoose()
    global sys_soft_list
    request_url = sys_soft_list[target_down]['DownLink']
    user_agent = sys_soft_list[target_down]['User-Agent']
    share_url = sys_soft_list[target_down]['Referer']
    cookie = sys_soft_list[target_down]['Cookie']
    host = sys_soft_list[target_down]['Host']
    # print('startDown running')
    data = None
    for i in range(5):
        data = parseDownloadLink(share_url, request_url, user_agent, cookie, host)
        if data != None:
            break

    # if data == None:
    #     tkinter.messagebox.showinfo('提示', '请检查网络连接，重新点击下载按钮')
    # else:
    #     tkinter.messagebox.showinfo('提示', '开始下载')
    # print(data.content)
    last_down_link = json.loads(data.content)['link']
    print(last_down_link)
    print(target_down)
    temp_fold = tempfile.gettempdir()

    th = threading.Thread(target=download, args=(last_down_link, temp_fold, target_down))
    th.setDaemon(True)  # 守护线程
    th.start()
    # download(last_down_link, temp_fold, target_down)


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
API_URL = None
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
btn_down = ttk.Button(down_frame, text='下载', command=startDown)
btn_pause = ttk.Button(down_frame, text='暂停')
label_down = ttk.Label(down_frame, text='下载进度')
bar_down = ttk.Progressbar(down_frame, length=100)
# bar_down = ttk.Label(down_fram, )
var_down = StringVar(down_frame)
var_down.set('0 KB/s')
label_speed = ttk.Label(down_frame, textvariable=var_down)

btn_down.grid(row=0, column=0)
btn_pause.grid(row=0, column=1)
label_down.grid(row=1, column=0)
bar_down.grid(row=1, column=1)
label_speed.grid(row=1, column=2)

currentValue = 0
bar_down["value"] = currentValue
bar_down["maximum"] = 100

# 设置安装界面
install_frame = Frame(root)
install_frame.pack()
btn_install = ttk.Button(install_frame, text='安装')
btn_install.grid(row=0)

root.mainloop()
