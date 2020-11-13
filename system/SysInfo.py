import platform
import psutil


def getSysInfo():
    sysname = platform.system()
    sysbits = platform.architecture()
    sysmem = psutil.virtual_memory().total
    return {'sysname': sysname, 'sysbits': sysbits, 'sysmem': sysmem}
