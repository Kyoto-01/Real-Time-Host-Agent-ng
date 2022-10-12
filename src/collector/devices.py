from collector import collect
from abc import ABC, abstractmethod


class SysDevice(ABC):

    '''
    Basic representation of a system device.
    '''

    def __init__(self, devName, context: 'dict' = None):
        self.name = devName

        if context:
            self.update(context)

    @staticmethod
    @abstractmethod
    def get_context() -> 'dict':
        '''
        returns a dictionary where each key represents a type of
        information and each value is a dictionary of devices with their
        respective data.

        Obs.: There should always be a 'devs' key, which contains
        the list where the device names will be taken from.
        this key must be a dictionary where each key is the name
        of a device (values are not taken into account).
        '''
        pass

    @abstractmethod
    def show(self) -> 'dict':
        '''
        Get the last updated device state.
        '''
        pass

    @abstractmethod
    def update(self, context: 'dict'):
        '''
        Updates device state based on a context.
        '''
        pass


class DevNetwork(SysDevice):

    '''
    Representation of a network interface
    '''

    def __init__(self, name, context=None):
        self.addr4 = None
        self.mask4 = None
        self.addr6 = None
        self.mask6 = None
        self.addrhw = None
        self.txPckts = None
        self.rxPckts = None

        super().__init__(name, context)

    @staticmethod
    def get_context():
        return {
            'devs': collect.net_if_addrs(),
            'ios': collect.net_io_counters(pernic=True),
            'stats': collect.net_if_stats(),
        }

    def show(self):
        return {
            'name': self.name,
            'addr4': self.addr4,
            'mask4': self.mask4,
            'addr6': self.addr6,
            'mask6': self.mask6,
            'addrhw': self.mac,
            'tx_pckts': self.txPckts,
            'rx_pckts': self.rxPckts,
        }

    def update(self, context):
        # Destructuring specific device contexts
        addrs = context['devs'][self.name]
        ios = context['ios'][self.name]
        #stats = context.stats[self.name]

        # Destructuring specific device context addressess
        addr4 = list(filter(lambda x: x.family == 2, addrs))
        addr6 = list(filter(lambda x: x.family == 10, addrs))
        addrhw = list(filter(lambda x: x.family == collect.AF_LINK, addrs))

        self.addr4 = addr4[0].address if addr4 else ''
        self.mask4 = addr4[0].netmask if addr4 else ''
        self.addr6 = addr6[0].address if addr6 else ''
        self.mask6 = addr6[0].netmask if addr6 else ''
        self.mac = addrhw[0].address if addrhw else ''
        self.txPckts = ios.packets_sent
        self.rxPckts = ios.packets_recv


class DevStrorage(SysDevice):

    '''
    Representation of a storage device
    '''

    def __init__(self, name, context=None):
        self.mountPoint = None
        self.filesystem = None
        self.total = None
        self.used = None
        self.free = None

        super().__init__(name, context)

    @staticmethod
    def get_context():
        devs = {dev.device: dev for dev in collect.disk_partitions()}

        return {
            'devs': devs,
        }

    def show(self):
        return {
            'name': self.name,
            'mount_point': self.mountPoint,
            'filesystem': self.filesystem,
            'total': self.total,
            'used': self.used,
            'free': self.free,
        }

    def update(self, context):
        # get device partition infos
        part = context['devs'][self.name]

        usage = collect.disk_usage(part.mountpoint)

        self.mountPoint = part.mountpoint
        self.filesystem = part.fstype
        self.total = usage.total
        self.used = usage.used
        self.free = usage.free
