import json
import os
import platform
import tempfile
import threading
import time
import tkinter.messagebox
from concurrent.futures.thread import ThreadPoolExecutor
from tkinter import *
from tkinter import ttk
from urllib.parse import unquote

import requests


# --------方法-----------
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


# 获得版本中的大版本数字
def getFirstNum(strnum):
    res = ""
    for i in strnum:
        if i.isdigit():
            res += i
        else:
            break
    return res


# 解析下载地址
def parseDownloadLink(SHARE_URL, REQUEST_URL, user_agent, cookie, host):
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
    global isDownloaded
    global canActive
    global isThreadActive
    isThreadActive = True
    canActive = True
    isDownloaded = False
    global file_path
    global file_name
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
        for chunk in r.iter_content(chunk_size=1024*1024*8):
            if not canActive:
                isThreadActive = False
                return

            startTime = time.time()
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                bar_down['value'] = 100 * temp_size / total_size
                info = "{}% {} KB/S".format(done, int(len(chunk)/1024/1024/(time.time()-startTime)))
                var_down.set(info)
                sys.stdout.write("\r[%s%s] %d%% %dKB/S" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size, int(len(chunk)/1024/1024/(time.time()-startTime))))
                sys.stdout.flush()
    print()  # 避免上面\r 回车符

    # 下载完成后，线程非活跃
    isThreadActive = False
    isDownloaded = True
    global btn_install
    btn_install['state'] = NORMAL

def stopDown():
    global canActive
    canActive = False

def installSoft():
    global file_path
    print(file_path)

# 开始下载
def startDown():
    global listbox
    chosen_down = listbox.get().split('【')[0]
    global sys_soft_list
    request_url = sys_soft_list[chosen_down]['DownLink']
    user_agent = sys_soft_list[chosen_down]['User-Agent']
    share_url = sys_soft_list[chosen_down]['Referer']
    cookie = sys_soft_list[chosen_down]['Cookie']
    host = sys_soft_list[chosen_down]['Host']
    global down_link
    for i in range(5):
        down_link = parseDownloadLink(share_url, request_url, user_agent, cookie, host)
        if down_link is not None:
            break

    if down_link is None:
        tkinter.messagebox.showinfo('提示', '请检查网络连接，重新点击下载按钮')
    else:
        tkinter.messagebox.showinfo('提示', '正在开始下载')

    down_link = json.loads(down_link.content)['link']
    print(down_link)
    # todo 磁盘不足
    temp_folder = tempfile.gettempdir()
    global thread1

    if not isThreadActive:
        thread1 = threading.Thread(target=download, args=(down_link, temp_folder, chosen_down))
        thread1.setDaemon(True)  # 守护线程
        thread1.start()



# ---------全局变量---------
thread1 = None
isDownloaded = False
canActive = True
isThreadActive = False
file_name = None
# executor = ThreadPoolExecutor(max_workers=1)
down_link = None
chosen_down = None
sys_bit = None
sys_name = None
APIs = {'win': 'http://tuduia.gitee.io/software-hub-api/win-ps.json',
        'mac': 'http://tuduia.gitee.io/software-hub-api/mac-ps.json'}
API_URL = None
sys_soft_list = None
request_data = None
listbox = None
file_path = None

# ---------启动获取相关信息-------
sys_bit = platform.architecture()[0]
sys_name = platform.system()
if sys_name == 'Darwin':
    sys_name = 'mac'
    API_URL = APIs['mac']
else:
    sys_name = 'win'
    API_URL = APIs['win']

# 网络请求软件清单
try:
    request_data = requests.get(API_URL)
except:
    pass

if request_data is not None and request_data.status_code == 200:
    sys_soft_list = json.loads(request_data.content)

# 创建窗口内容
root = Tk()
root.title('PS/PhotoShop一键安装程序')
width = 500
heigth = 400
root.geometry('{}x{}'.format(width, heigth))

# ---------控件变量---------
down_frame = Frame(root)

# 版本选择
text_startup = StringVar()
get_list_btn = ttk.Button(down_frame, text='重新获取')
listbox = ttk.Combobox(down_frame, state='readonly')
label_startup = ttk.Label(down_frame, textvariable=text_startup)

# 下载控件
btn_down = ttk.Button(down_frame, text='下载', command=startDown)
btn_pause = ttk.Button(down_frame, text='暂停', command=stopDown)

# 下载进度
label_down = ttk.Label(down_frame, text='下载进度')
var_down = StringVar(down_frame)
var_down.set('0% 0 KB/s')
bar_down = ttk.Progressbar(down_frame, length=100)
label_speed = ttk.Label(down_frame, textvariable=var_down)

btn_install = ttk.Button(down_frame, text='安装', state=DISABLED)
# 状态信息
state_text = StringVar()
# state_text.set('Welcome')
label_state = ttk.Label(down_frame, textvariable=state_text)

# 步骤
step1 = ttk.Label(down_frame, text='第一步:')
step2 = ttk.Label(down_frame, text='第二步:')
step3 = ttk.Label(down_frame, text='第三步:')
var_2 = StringVar()
var_3 = StringVar()

step1.grid(row=0, column=0, columnspan=10, sticky=N + S, pady=10)

if sys_soft_list is None:
    text_startup.set('请检查网络连接，点击下方按钮重新获取')
    listbox.set('请点击按钮重新获取')
    btn_down['state'] = DISABLED
    btn_pause['state'] = DISABLED
    label_startup.grid(row=1, columnspan=10, sticky=N + S)
    listbox.grid(row=2, column=0, columnspan=7, sticky=N + S, pady=10)
    get_list_btn.grid(row=2, column=8, columnspan=2, sticky=N + S, pady=10)
else:
    text_startup.set('已成功获取您电脑可以运行的版本，请选择')
    var_2.set('请点击下方的【下载】按钮，下载相关文件')
    label_startup.grid(row=1, columnspan=10, sticky=N + S)
    state_text.set('请选择版本后，点击【下载】按钮')
    # 提取合适的版本
    # sys_soft_list 所有软件列表清单

    listbox['value'] = all2suit(sys_soft_list)
    listbox.set(all2suit(sys_soft_list)[0])
    listbox.grid(row=2, column=0, columnspan=10, sticky=N + S, pady=10)

step2.grid(row=3, column=0, columnspan=10, sticky=N + S, pady=10)
label_2 = ttk.Label(down_frame, textvariable=var_2)
label_2.grid(row=4, column=0, columnspan=10, sticky=N + S)

btn_down.grid(row=5, column=0, columnspan=4, sticky=N + S)
btn_pause.grid(row=5, column=5, columnspan=4, sticky=N + S)
label_down.grid(row=6, column=0, columnspan=2, sticky=N + S, pady=10)
bar_down.grid(row=6, column=3, columnspan=4, sticky=N + S, pady=10)
label_speed.grid(row=6, column=8, columnspan=2, pady=10)

var_3.set('请先下载，下载后即可进行安装')
step3.grid(row=7, column=0, columnspan=10, sticky=N + S, pady=10)
label_3 = ttk.Label(down_frame, textvariable=var_3)
label_3.grid(row=8, column=0, columnspan=10, sticky=N + S)
btn_install.grid(row=9, column=0, columnspan=10, sticky=N + S, pady=10)

down_frame.pack(expand=1)

root.mainloop()
