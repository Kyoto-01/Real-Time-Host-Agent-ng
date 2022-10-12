from collector.devices import *


class SysResource(ABC):

    '''
    Basic representation of a system resource. System resources
    are information pertaining to a set of devices.
    '''

    def __init__(self):
        self.update()

    def collect(self) -> 'dict':
        '''
        Get the current resource state.
        '''
        self.update()
        return self.show()

    @abstractmethod
    def show(self) -> 'dict':
        '''
        Get the last updated resource state.
        '''
        pass

    @abstractmethod
    def update(self):
        '''
        Update resource state.
        '''
        pass


class ResDevGrouper(SysResource):

    '''
    Resources based on a group of same type SysDevice objects.
    '''

    DEV_TYPE: SysDevice = None

    def __init__(self, devType):
        self.devices = []

        self.__class__.DEV_TYPE = devType
        self.poll()

    def poll(self):
        '''
        Hard update that also lets you load new devices
        '''
        context = self.__class__.DEV_TYPE.get_context()

        self.devices.clear()

        for dev in context['devs']:
            self.devices.append(self.__class__.DEV_TYPE(dev, context))

    def show(self):
        return [dev.show() for dev in self.devices]

    def update(self):
        '''
        Soft update for loaded devices
        '''
        context = self.__class__.DEV_TYPE.get_context()

        for dev in self.devices:
            if (name := dev.name) in context['devs']:
                dev.update(context)


class ResCPU(SysResource):

    '''
    Processing resources
    '''

    def __init__(self):
        self.architecture = None
        self.modelName = None
        self.phyCores = None
        self.logCores = None
        self.threadsCore = None
        self.sockets = None
        self.used = None
        self.temperature = None
        self.clock = None
        self.clockMax = None
        self.clockMin = None

        super().__init__()

    def show(self):
        return {
            'architecture': self.architecture,
            'model_name': self.modelName,
            'phy_cores': self.phyCores,
            'log_cores': self.logCores,
            'threads_core': self.threadsCore,
            'sockets': self.sockets,
            'used': self.used,
            'temperature': self.temperature,
            'clock': self.clock,
            'clock_max': self.clockMax,
            'clock_min': self.clockMin,
        }

    def update(self):
        clocks = collect.cpu_freq()

        self.architecture = collect.machine()
        self.modelName = collect.cpu_model_name()
        self.phyCores = collect.cpu_count(False)
        self.logCores = collect.cpu_count()
        self.threadsCore = (int)(self.logCores / self.phyCores)
        self.sockets = collect.cpu_socket_number()
        self.used = collect.cpu_percent()
        self.temperature = collect.cpu_temperature()
        self.clock = clocks.current
        self.clockMax = clocks.max
        self.clockMin = clocks.min


class ResMemory(SysResource):

    '''
    Memory resources
    '''

    def __init__(self):
        self.total = None
        self.used = None
        self.free = None
        self.shared = None
        self.cached = None
        self.available = None
        self.totalSwap = None
        self.usedSwap = None
        self.freeSwap = None

        super().__init__()

    def show(self):
        return {
            'total': self.total,
            'used': self.used,
            'free': self.free,
            'shared': self.shared,
            'cached': self.cached,
            'available': self.available,
            'total_swap': self.totalSwap,
            'used_swap': self.usedSwap,
            'free_swap': self.freeSwap,
        }

    def update(self):
        virt = collect.virtual_memory()
        swap = collect.swap_memory()

        self.total = virt.total
        self.used = virt.used
        self.free = virt.free
        self.shared = virt.shared
        self.cached = virt.cached
        self.available = virt.available
        self.totalSwap = swap.total
        self.usedSwap = swap.used
        self.freeSwap = swap.free


class ResSystem(SysResource):

    '''
    Operating System resources
    '''

    def __init__(self):
        self.os = None
        self.hostname = None

        super().__init__()

    def show(self):
        return {
            'os': self.os,
            'hostname': self.hostname,
        }

    def update(self):
        self.hostname = collect.node()
        self.os = collect.system()


class ResMachine(SysResource):

    '''
    Machine hardware and software resources
    '''

    def __init__(self):
        self.system = ResSystem()
        self.memory = ResMemory()
        self.cpu = ResCPU()
        self.network = ResDevGrouper(DevNetwork)
        self.storage = ResDevGrouper(DevStrorage)

        super().__init__()

    def show(self):
        return {
            'system': self.system.show(),
            'memory': self.memory.show(),
            'cpu': self.cpu.show(),
            'network': self.network.show(),
            'storage': self.storage.show(),
        }

    def update(self):
        self.system.update()
        self.memory.update()
        self.cpu.update()
        self.network.update()
        self.storage.update()
