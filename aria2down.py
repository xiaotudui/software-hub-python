import os
import subprocess

DownLink = "https://static.cowtransfer.com/cloud-14ec36d1-4111-4c9e-ab38-b4f99cfa95f9%2F%E7%9C%9FAdobe%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%2FAe2018-2020%2FAe_2020.exe?t-s=1604999170042&t-c=a4a36db8-7816-407e-8ad1-baaa2bbf6261"
cmd = './aria2c-mac \"{}\"'.format(DownLink)

# info = os.popen(cmd)
# for i in info:
#     print(i)

# p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
# print("---正在飞速下载软件---")
# msg_content = ''
# for line in p1.stdout:
#     print(line)
#     l = line.decode(encoding="utf-8", errors="ignore")



