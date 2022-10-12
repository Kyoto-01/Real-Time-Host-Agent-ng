import subprocess

from platform import *
from psutil import *

OS_NAME = system()


def cpu_model_name():
    name = ''

    if OS_NAME == 'Linux':
        cmd = 'cat /proc/cpuinfo | grep "model name" | head -1 | cut -d ":" -f 2'
        name = subprocess.check_output(cmd, shell=True).decode()
    elif OS_NAME == 'Darwin':
        cmd = '/usr/sbin/sysctl -n machdep.cpu.brand_string'
        name = subprocess.check_output(cmd, shell=True).decode()
    else:
        name = processor()

    return name.strip()


def cpu_socket_number():
    nsckts = 1

    if OS_NAME == 'Linux':
        cmd = 'cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l'
        nsckts = int(subprocess.check_output(cmd, shell=True).decode())

    return nsckts


def cpu_temperature():
    return 0
