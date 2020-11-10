import platform
import psutil

def getSysInfo():
    sysname = platform.system()
    print(platform.machine())
    sysbits = platform.architecture()
    sysmem = psutil.virtual_memory().total
    print(sysname)
    print(sysbits)
    print(sysmem)


def main():
    getSysInfo()

if __name__ == '__main__':
    main()
