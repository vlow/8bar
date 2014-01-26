#import configparser
import subprocess
import time
import psutil

"""
    This first draft plays with some concepts like different update
    timings and string-based layout templates.

    There is still a lot to do: Configuration has to be loaded from
    a config file via configparser (also general dzen configuration),
    most built-in functions are missing, users should be able to
    load plug-ins easily and there is a lot of code clean-up to do.
"""


class StringGenerator(object):
    information_cache = []
    parameter = []
    timestamps = []
    objects = []

    def __init__(self, layout, objects):
        currentTimestamp = 0
        self.objects = objects
        for x in range(0, len(layout)):
            self.information_cache.append("")
            self.timestamps.append(currentTimestamp)
        self.layout = layout
        return

    def createString(self):
        returnString = self.layout
        for i in range(0, len(self.objects)):
            if time.time() - self.timestamps[i] > self.objects[i]["Timing"]:
                self.timestamps[i] = time.time()
                self.information_cache[i] = self.objects[i]["Function"]
                (self.objects[i]["Parameters"])
            returnString = returnString.replace("$%s$" % self.objects[i]
                                                ["Identifier"],
                                                self.information_cache[i])
            continue
        return returnString


# built-in functions (just some PoCs for now)
def formatedClock(parameterDict):
    return time.strftime(parameterDict["Format"])


def externalCommand(parameterDict):
    commandList = [parameterDict["commandName"]]
    command = commandList + parameterDict["argsList"]
    return str(subprocess.check_output(command), "UTF-8").replace("\n", "")


def free_memory(parameterDict):
    ram = psutil.phymem_usage()
    free_ram = ram.free/(1024*1024)
    return "%0.2f" % free_ram


def total_memory(parameterDict):
    ram = psutil.phymem_usage()
    total_ram = ram.total/(1024*1024)
    return "%0.2f" % total_ram


def free_memory_percentage(parameterDict):
    ram = psutil.phymem_usage()
    free_ram = ram.free/(1024*1024)
    total_ram = ram.total/(1024*1024)
    return "%0.2f" % ((free_ram/total_ram)*100) + " %"


def used_memory_percentage(parameterDict):
    ram = psutil.phymem_usage()
    used_ram = ram.used/(1024*1024)
    total_ram = ram.total/(1024*1024)
    return "%0.2f" % ((used_ram/total_ram)*100) + " %"


# this doesn't really work yet, because cpu-usages are returned as a list
def cpu_usage(parameterDict):
    cpu = psutil.cpu_times_percent(interval=0, percpu=True)
    returnValue = []
    for x in range(0, len(cpu)):
        returnValue.append("%0.2f" % (100-cpu[x][3]) + " %")
    return returnValue

# some testing definitions (these will not be needed once configuration-file
# support is implemented
my_command_parameters = {"commandName": "uname", "argsList": ["-a"]}
my_command = {"Object": "externalCommand", "Identifier": "externalCommand1",
              "Timing": 3, "Function": externalCommand,
              "Parameters": my_command_parameters}
my_clock_parameters = {"Format": "%H:%M:%S"}
my_clock = {"Object": "clock", "Timing": 2, "Identifier": "clock",
            "Function": formatedClock, "Parameters": my_clock_parameters}
my_freeram = {"Object": "free_ram", "Timing": 1, "Identifier": "free_ram",
              "Function": free_memory, "Parameters": []}
my_objects = [my_clock, my_freeram, my_command]
my_layout = "$clock$ | Free RAM: $free_ram$ MB | Kernel: $externalCommand1$"

# the general running logic - just a stub right now
# exception handling needs to be implemented
myCreator = StringGenerator(my_layout, my_objects)
dzen = subprocess.Popen(['dzen2', '-fn', 'Terminus'], stdin=subprocess.PIPE)
while(dzen.pid):
    dzen.stdin.write(bytes(myCreator.createString()+"\n", "UTF-8"))
    dzen.stdin.flush()
    time.sleep(1)
