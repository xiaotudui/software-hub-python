import json
import platform
import time
from tkinter import *
from tkinter import ttk

import psutil
import requests


class ChoosePage(object):
    def __init__(self, master=None):
        self.root = master  # 定义内部变量root
        self.height = 500
        self.width = 400
        self.root.geometry('%dx%d' % (self.width, self.height))  # 设置窗口大小
        self.page = Frame(self.root)
        self.page.pack()
        self.createPage()


    def createPage(self):
        self.createChooseList()
        self.createDownPage()


    def createChooseList(self):
        chooseFrame = Frame(self.page)
        chooseFrame.grid()
        label = Label(self.page, text='请选择您需要安装的版本')
        label.grid(row=0)
        listbox = ttk.Combobox(self.page)
        listbox.grid(row=1)

        soft_list = self.canGetList()


        # 如果请求失败
        if soft_list == None:
            button = ttk.Button(self.page, text='请求')
            button.grid(row=1, column=1)
        #  请求成功，填充
        else:
            soft_list = self.canDownList(soft_list)
            # for item in soft_list:
            #     print(item)
            #     print(type(item))
            listbox['value'] = soft_list


    def createDownPage(self):
        downFrame = Frame(self.page)
        downFrame.grid()
        downbtn = ttk.Button(downFrame, text='下载')
        downbtn.grid(row=0)






    def canDownList(self, jsonInfo):
        downlist = []
        sysname = platform.system()
        sysbit = platform.architecture()[0]
        if sysname == 'Darwin':
            sysname = 'mac'
            sysbit = '64'
        else:
            sysname = 'win'

        # 调整格式，系统写法mac，win7

        for key, value in jsonInfo.items():
            if sysname in value['requirements'] and sysbit in value['requirements']:
                if 'recommend' in value['requirements']:
                    downlist.insert(0, key+'【推荐】')
                else:
                    downlist.append(key)
        return downlist


    def canGetList(self):
        # 获取软件所有信息
        APIs = {'win': 'http://tuduia.gitee.io/software-hub-api/win-ps.json',
                'mac': 'http://tuduia.gitee.io/software-hub-api/mac-ps.json'}

        sysname = platform.system()
        if sysname.lower() == 'windows':
            API_URL = APIs['win']
        elif sysname.lower() == 'darwin':
            API_URL = APIs['mac']
        else:
            print('Not Support operations')

        # 网络请求
        data = requests.get(API_URL)
        for i in range(5):
            if data.status_code == 200:
                jsonObject = json.loads(data.content)
                return jsonObject
            else:
                # print('网络异常，正在重试 [{}/10]'.format(i + 1))
                time.sleep(5)

        # print("网络异常，请稍后重试或联系客服")


    def getSysInfo(self):
        sysname = platform.system()
        sysbits = platform.architecture()
        sysmem = psutil.virtual_memory().total
        return {'sysname': sysname, 'sysbits': sysbits, 'sysmem': sysmem}




