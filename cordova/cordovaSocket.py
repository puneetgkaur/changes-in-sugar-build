
import sys
import logging

import device as cordova_Device
import accelerometer as cordova_Accelerometer
import camera as cordova_Camera
import network as cordova_Network
import dialog as cordova_Dialog
import language as cordova_Language


#plugin={'accelerometer':{cordova_accelerometer.accelerometer_obj},'camera':{'journal':,'camera':cordova_camera.pygame_camera()},'device':{},'dialog':{},'globalization':{},'network':{}}


class callCordova(object):

    def call_to_cordova(self,plugin_name,function_name,args,parent,request):
        plugin_filecode= getattr(sys.modules[__name__],"cordova_"+plugin_name)
        logging.error(plugin_filecode)
        #constructor = globals()[plugin_name]() # the class name for the plugin must be same as the plugin name
        plugin_class = getattr(plugin_filecode,plugin_name)()
        logging.error(plugin_class)
        service_method = getattr(plugin_class,function_name) # The service method must same as that described for the given class
        logging.error(service_method)
        result = service_method(args,parent,request) # give the parameters in args
        return result


        if (plugin_name == "accelerometer"):
            logging.error("request : %s",request)
            acc_obj=cordova_accelerometer.accelerometer_obj()
            return acc_obj

        elif (plugin_name == "camera"):
            logging.error("cordova_camera:%s",request)
            if request['params'][0]=='webcam' :
                logging.error("record: %s",self._activity)
                filename=cordova_camera.pygame_camera()
                self._client.send_result(request,cordova_camera.conversionToBase64(filename))
            elif request['params'][0]=='image_chooser' :
                image_chooser=cordova_camera.choose_image(self,request)
                image_chooser.show_image_chooser(self)
            elif request['params'][0]=='conversionToBase64':
                self._client.send_result(request,cordova_camera.conversionToBase64('/home/broot/Documents/Photo by broot.jpe'))
            else:
                self._client.send_result(request,"Wrong option")

        elif (plugin_name == "dialog"):
            if request['params'][0]=='alert' :
                title=request['params'][2]
                buttonLabel=request['params'][3][0]
                message=request['params'][1]
                logging.error("in cordova_DialogPlugin 1:%s",request['params'][1])
                logging.error("in cordova_DialogPlugin 2:%s",request['params'][2])
                logging.error("in cordova_DialogPlugin 3:%s",request['params'][3][0])
                cordova_dialog.show_dialog(self,request,'alert',message,title,buttonLabel)
            elif request['params'][0]=='confirm':
                message=request['params'][1]
                title=request['params'][2]
                buttonLabel=request['params'][3]
                logging.error("in cordova_DialogPlugin 1:%s",request['params'][1])
                logging.error("in cordova_DialogPlugin 2:%s",request['params'][2])
                logging.error("in cordova_DialogPlugin 3:%s",request['params'][3])
                cordova_dialog.show_dialog(self,request,'confirm',message,title,buttonLabel)
            elif request['params'][0]=='prompt' :
                message=request['params'][1]
                title=request['params'][2]
                buttonLabel=request['params'][3]
                defaultText=request['params'][4]
                logging.error("in cordova_DialogPlugin 1:%s",request['params'][1])
                logging.error("in cordova_DialogPlugin 2:%s",request['params'][2])
                logging.error("in cordova_DialogPlugin 3:%s",request['params'][3])
                logging.error("in cordova_DialogPlugin 4:%s",request['params'][4])
                cordova_dialog.show_dialog(self,request,'prompt',message,title,buttonLabel,defaultText)            
            elif request['params'][0]=='beep':
                self._client.send_error(request,"trying to come up with this option")
            else:
                self._client.send_error(request,"Wrong option")


        elif (plugin_name == "device"):
            logging.error("cordova_device:%s",request)
            if request['params'][0]=='sugar_version':
                logging.error("device version : %s", cordova_device.get_sugar_version())
                self._client.send_result(request,cordova_device.get_sugar_version())
            elif request['params'][0]=='sugar_model':
                self._client.send_result(request,cordova_device.get_hardware_model())
            elif request['params'][0]=='sugar_uuid' :
                self._client.send_result(request,cordova_device.get_uuid())
            else:
                self._client.send_result(request,"Wrong option")


        elif (plugin_name == "globalization"):
            pass

        elif (plugin_name == "network"):
            pass
