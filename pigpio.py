import subprocess


OUT = 'out'
IN = 'in'

CMD_EXPORT = 'echo {index} > /sys/class/gpio/export'
CMD_UNEXPORT = 'echo {index} > /sys/class/gpio/unexport'
CMD_DIRECTION = 'echo {direction} > /sys/class/gpio/gpio{index}/direction'
CMD_OUTPUT = 'echo {value} > /sys/class/gpio/gpio{index}/value'
CMD_INPUT = 'cat /sys/class/gpio/gpio{index}/value'


def setup(index, direction):
    commands = (CMD_EXPORT.format(index=index),
                CMD_DIRECTION.format(direction=direction, index=index))
    for command in commands:
        subprocess.call([command], shell=True)


def output(index, value):
    command = CMD_OUTPUT.format(index=index, value=1 if value else 0)
    subprocess.call([command], shell=True)


def input(index):
    command = CMD_INPUT.format(index=index)
    value = int(subprocess.check_output([command], shell=True))
    return True if value else False
