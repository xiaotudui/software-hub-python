import sys
import time

import requests
import os

# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()

def download(url, file_path):
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    print(r1.headers)
    total_size = int(r1.headers['Content-Length'])

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
            startTime = time.time()
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()

                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%% %dKB/S" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size, int(len(chunk)/1024/1024/(time.time()-startTime))))
                sys.stdout.flush()
    print()  # 避免上面\r 回车符


if __name__ == '__main__':
    url = 'https://static.cowtransfer.com/cloud-14ec36d1-4111-4c9e-ab38-b4f99cfa95f9%2F%E7%9C%9FAdobe%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%2FAe2018-2020%2FAe_2020.exe?t-s=1604993291273&t-c=34cb8804-f12a-487e-824c-cb94c0ad0649'
    path = './ps2020.zip'
    # 调用一下函数试试
    download(url, path)
