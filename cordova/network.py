from jarabe.model import network
import dbus
import logging


_DBUS_SERVICE = 'org.sugarlabs.SugarServices'
_DBUS_PATH = '/org/sugarlabs/SugarServices'

proxy=None

def get_network_type(parent,request):
    #network_connection_obj=network.get_connections()
    #network_connections=network_connection_obj.get_list()
    #logging.error("network connections : %s",network_connections)
    #logging.error("network._get_settings : %s",network._get_settings())
    type_network = NetworkManagerObserver(parent,request)
    #logging.error("the type of network : %s",type_network)


def nm_status():
    global proxy
    if proxy is None:
        bus = dbus.SessionBus()
        proxy = bus.get_object(_DBUS_SERVICE, _DBUS_PATH)

    try:
        status = dbus.Interface(proxy, _DBUS_SERVICE).NMStatus()
        logging.debug(status)
        return status
    except Exception, e:
        logging.error('ERROR getting NM Status: %s' % e)
        return None

    if status in ['network-wireless-connected',
                  'network-wireless-disconnected',
                  'network-adhoc-1-connected',
                  'network-adhoc-1-disconnected',
                  'network-adhoc-6-connected',
                  'network-adhoc-6-disconnected',
                  'network-adhoc-11-connected',
                  'network-adhoc-11-disconnected']:
        return status
    else:
        return 'unknown'



# The Network Manager Class from sugar/extensions/deviceicon
class NetworkManagerObserver(object):
    def __init__(self,parent,request):
        self.parent=parent
        self.request=request
        self._bus = dbus.SystemBus()
        self._devices = {}
        self._netmgr = None
        #self._tray = tray
        self.type_network="unknown"

        try:
            obj = self._bus.get_object(network.NM_SERVICE, network.NM_PATH)
            self._netmgr = dbus.Interface(obj, network.NM_IFACE)
        except dbus.DBusException:
            logging.error('%s service not available', network.NM_SERVICE)
            return

        self._netmgr.GetDevices(reply_handler=self.__get_devices_reply_cb,
                                error_handler=self.__get_devices_error_cb)

        self._bus.add_signal_receiver(self.__device_added_cb,
                                      signal_name='DeviceAdded',
                                      dbus_interface=network.NM_IFACE)
        self._bus.add_signal_receiver(self.__device_removed_cb,
                                      signal_name='DeviceRemoved',
                                      dbus_interface=network.NM_IFACE)

    def __get_devices_reply_cb(self, devices):
        for device_op in devices:
            self._check_device(device_op)

    def __get_devices_error_cb(self, err):
        logging.error('Failed to get devices: %s', err)

    def _check_device(self, device_op):
        #if device_op in self._devices:
        #    return

        nm_device = self._bus.get_object(network.NM_SERVICE, device_op)
        props = dbus.Interface(nm_device, dbus.PROPERTIES_IFACE)

        device_type = props.Get(network.NM_DEVICE_IFACE, 'DeviceType')
        if device_type == network.NM_DEVICE_TYPE_ETHERNET:
            logging.error("type of network connection - ethernet")
            self.type_network = "ethernet"
            #device = WiredDeviceObserver(nm_device, self._tray)
            #self._devices[device_op] = "ethernet"
        elif device_type == network.NM_DEVICE_TYPE_WIFI:
            logging.error("type of network connection - wi-fi")
            self.type_network = "wifi"
            #device = WirelessDeviceObserver(nm_device, self._tray)
            #self._devices[device_op] = "wi-fi"
        elif device_type == network.NM_DEVICE_TYPE_OLPC_MESH:
            logging.error("type of network connection - olpc-mesh")
            self.type_network = "olpcmesh"
            #device = MeshDeviceObserver(nm_device, self._tray)
            #self._devices[device_op] = "olpc - mesh"
        elif device_type == network.NM_DEVICE_TYPE_MODEM:
            logging.error("type of network connection - modem")
            self.type_network = "cellular"
            #device = GsmDeviceObserver(nm_device, self._tray)
            #self._devices[device_op] = "cellular"
        else :
            logging.error("no connection")
            self.type_network = "none"            
        #self.parent._client.send_result(self.request,self.type_network)

    def __device_added_cb(self, device_op):
        self._check_device(device_op)

    def __device_removed_cb(self, device_op):
        logging.error("in remove device event")
        """
        if device_op in self._devices:
            device = self._devices[device_op]
            device.disconnect()
            del self._devices[device_op]
        """

