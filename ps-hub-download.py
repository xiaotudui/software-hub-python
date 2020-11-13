import platform
import subprocess
import psutil
import requests
import json
import time


def parseDownloadLink(SHARE_URL, REQUEST_URL, user_agent, cookie, host):
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie,
        'Host': host,
        'Referer': SHARE_URL
    }
    data = requests.post(REQUEST_URL, headers=headers)
    print(data.content)
    return json.loads(data.content)


def getURLInfo(API_URL: str):
    data = requests.get(API_URL)
    for i in range(10):
        if data.status_code == 200:
            jsonObject = json.loads(data.content)
            return jsonObject
        else:
            print('网络异常，正在重试 [{}/10]'.format(i+1))
            time.sleep(5)
    print("网络异常，请稍后重试或联系客服")


def getSysInfo():
    sysname = platform.system()
    sysbits = platform.architecture()
    sysmem = psutil.virtual_memory().total
    return {'sysname': sysname, 'sysbits': sysbits, 'sysmem': sysmem}


def byte2GB(byte):
    return byte/1024/1024/1024


def byte2MB(byte):
    return byte/1024/1024


def canDownList(jsonInfo, sysinfo):
    downlist = []
    sysbits = sysinfo['sysbits']
    sysname = sysinfo['sysname']
    sysmem = sysinfo['sysmem']
    print(jsonInfo)

    for key, value in jsonInfo.items():
        if True:
            downlist.append(key)
    return downlist


def startAria2c(DownLink, savePath, chosenname):
    # cmd = './aria2c-mac ' + DownLink
    cmd = './aria2c-mac \"{}\"'.format(DownLink)
    print(cmd)

    try:
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        print("---正在飞速下载软件---")
        msg_content = ''
        for line in p1.stdout:
            print(line)
            l = line.decode(encoding="utf-8", errors="ignore")
            msg_content += 1
        p1.wait()
        if '(OK):download completed' in msg_content:
            print("download by aira2 successfully.")
            return True
        return False
    except Exception as e:
        print(e)
        return False


def valiate(number):
    target = time.time()




def main():
    sysinfo = getSysInfo()
    print("您的系统为：" + sysinfo['sysname'] + "内存大小为: " + str(byte2GB(sysinfo['sysmem']))+"GB")

    APIs = {'win': 'http://tuduia.gitee.io/software-hub-api/win-ps.json',
            'mac': 'http://tuduia.gitee.io/software-hub-api/mac-ps.json'}

    API_URL = ''

    # 确定操作系统和请求的API地址
    if sysinfo['sysname'].lower() == 'windows':
        API_URL = APIs['win']
    elif sysinfo['sysname'].lower() == 'darwin':
        API_URL = APIs['mac']
    else:
        print('Not Support operations')

    # 请求API获取软件库信息
    print('正在连接【资源库】，获取您电脑可用的软件清单')
    hubInfo = getURLInfo(API_URL)
    # print(hubInfo)
    # print(type(hubInfo))
    print(canDownList(hubInfo, sysinfo))

    chosedown = 'ps2020'

    # 获取指定版本的下载链接
    user_agent = hubInfo[chosedown]['User-Agent']
    cookie = hubInfo[chosedown]['Cookie']
    host = hubInfo[chosedown]['Host']
    referer = hubInfo[chosedown]['Referer']
    requestLink = hubInfo[chosedown]['DonwLink']
    shareLink = referer
    downLink = parseDownloadLink(shareLink, requestLink, user_agent, cookie, host)
    print(downLink['link'])

    startAria2c(str(downLink['link']), '', '')



if __name__ == '__main__':
    print('欢迎使用，一键安装Photoshop程序')
    main()

