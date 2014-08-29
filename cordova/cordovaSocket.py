
import sys
import logging

import device as cordova_Device
import accelerometer as cordova_Accelerometer
import camera as cordova_Camera
import network as cordova_Network
import dialog as cordova_Dialog
import globalization as cordova_Globalization


#plugin={'accelerometer':{cordova_accelerometer.accelerometer_obj},'camera':{'journal':,'camera':cordova_camera.pygame_camera()},'device':{},'dialog':{},'globalization':{},'network':{}}


class callCordova(object):

    def call_to_cordova(self,plugin_name,function_name,args,parent,request):
        try:
            plugin_filecode= getattr(sys.modules[__name__],"cordova_"+plugin_name)
            logging.error(plugin_filecode)
            #constructor = globals()[plugin_name]() # the class name for the plugin must be same as the plugin name
            plugin_class = getattr(plugin_filecode,plugin_name)()
            logging.error(plugin_class)
            service_method = getattr(plugin_class,function_name) # The service method must same as that described for the given class
            logging.error(service_method)
            result = service_method(args,parent,request) # give the parameters in args
            return result
        except:
            parent._client.send_error(request,"The native function does not exist")

