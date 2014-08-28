# Copyright (C) 2013, Daniel Narvaez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import json
import os
import struct
import time
import sys
import dbus
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gio
from gwebsockets.server import Server
from gwebsockets.server import Message

from sugar3 import env

from jarabe.model import shell
from jarabe.model import session
from jarabe.journal.objectchooser import ObjectChooser

import logging

from jarabe.cordova import device as cordova_device
from jarabe.cordova import accelerometer as cordova_accelerometer
from jarabe.cordova import camera as cordova_camera
from jarabe.cordova import network as cordova_network
from jarabe.cordova import dialog as cordova_dialog
from jarabe.cordova import language as cordova_language

from jarabe.cordova import cordovaSocket

class StreamMonitor(object):
    def __init__(self):
        self.on_data = None
        self.on_close = None


class API(object):
    def __init__(self, client):
        self._client = client

        self._activity = None
        for activity in shell.get_model():
            if activity.get_activity_id() == client.activity_id:
                self._activity = activity


class ActivityAPI(API):
    def __init__(self, client):
        API.__init__(self, client)
        self._activity.connect('pause', self._pause_cb)
        self._activity.connect('resume', self._resume_cb)
        self._activity.connect('stop', self._stop_cb)

        session.get_session_manager().shutdown_signal.connect(
            self._session_manager_shutdown_cb)

    def get_xo_color(self, request):
        settings = Gio.Settings('org.sugarlabs.user')
        color_string = settings.get_string('color')

        self._client.send_result(request, [color_string.split(",")])

    def close(self, request):
        self._activity.get_window().close(GLib.get_current_time())

        self._client.send_result(request, [])

    def _pause_cb(self, event):
        self._client.send_notification("activity.pause")

    def _resume_cb(self, event):
        self._client.send_notification("activity.resume")

    def _stop_cb(self, event):
        # When the web activity receives this notification, it has
        # time for saving the state and do any cleanup needed.  Then
        # it must call 'window.close' to complete the activity
        # closing.
        self._client.send_notification("activity.stop")
        return True

    def _session_manager_shutdown_cb(self, event):
        self._client.send_notification("activity.stop")


    def show_object_chooser(self, request):
        chooser = ObjectChooser(self._activity)
        chooser.connect('response', self._chooser_response_cb, request)
        chooser.show()

    def _chooser_response_cb(self, chooser, response_id, request):
        if response_id == Gtk.ResponseType.ACCEPT:
            object_id = chooser.get_selected_object_id()
            self._client.send_result(request, [object_id])
        else:
            self._client.send_result(request, [None])
        chooser.destroy()

    def cordova(self,request):
        plugin_name=request['params'][0]
        service_name=request['params'][1]
        args=request['params'][2]
        cordova_class=cordovaSocket.callCordova()
        cordova_class.call_to_cordova(plugin_name,service_name,args,self,request)


    """
    def cordova_AccelerometerPlugin(self,request):
        logging.error("request : %s",request)
        acc_obj=cordova_accelerometer.accelerometer_obj()
        self._client.send_result(request,acc_obj)

    
    def cordova_CameraPlugin(self,request):
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


    def cordova_DevicePlugin(self,request):
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
    

    def cordova_NetworkPlugin(self,request):
        ""
        logging.error("********cordova_NetworkPlugin**********")
        logging.error("self:")
        logging.error(self)
        logging.error("request:")
        logging.error(request)
        network_type= cordova_network.get_network_type(self,request)
        logging.error("*************network_type**************")
        logging.error(network_type)
        ""
        logging.error("cordova_network_type_name is")
        logging.error(cordova_network.network_type_name) 
        self._client.send_result(request,cordova_network.network_type_name)

    def cordova_DialogPlugin(self,request):
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



    def cordova_GlobalizationPlugin(self,request):
        if request['params'][0]=='getPreferredLanguage' :
            preferred_language=cordova_language.get_preferred_language()
            logging.error("The preferred_language : %s",preferred_language)
            self._client.send_result(request,{"value":preferred_language})
        elif request['params'][0]=='getLocaleName' :
            locale_name=cordova_language.get_locale_name()
            logging.error("The preferred_language : %s",locale_name)
            self._client.send_result(request,{"value":locale_name})
        else:
            self._client.send_error(request,"Wrong option")

    """


class DatastoreAPI(API):
    def __init__(self, client):
        API.__init__(self, client)

        bus = dbus.SessionBus()
        bus_object = bus.get_object("org.laptop.sugar.DataStore",
                                    "/org/laptop/sugar/DataStore")
        self._data_store = dbus.Interface(bus_object,
                                          "org.laptop.sugar.DataStore")

    def _create_file(self):
        activity_root = env.get_profile_path(self._activity.get_type())
        instance_path = os.path.join(activity_root, "instance")

        file_path = os.path.join(instance_path, "%i" % time.time())
        file_object = open(file_path, "w")

        return file_path, file_object

    def get_metadata(self, request):
        def get_properties_reply_handler(properties):
            self._client.send_result(request, [properties])

        def error_handler(error):
            self._client.send_error(request, error)

        self._data_store.get_properties(
            request["params"][0], byte_arrays=True,
            reply_handler=get_properties_reply_handler,
            error_handler=error_handler)

    def set_metadata(self, request):
        def reply_handler():
            self._client.send_result(request, [])

        def error_handler(error):
            self._client.send_error(request, error)

        uid, metadata = request["params"]

        self._data_store.update(uid, metadata, "", True,
                                reply_handler=reply_handler,
                                error_handler=error_handler)

    def load(self, request):
        def get_filename_reply_handler(file_name):
            file_object = open(file_name)
            info["file_object"] = file_object

            if "requested_size" in info:
                send_binary(file_object.read(info["requested_size"]))

            if "stream_closed" in info:
                info["file_object"].close()

        def get_properties_reply_handler(properties):
            self._client.send_result(request, [properties])

        def error_handler(error):
            self._client.send_error(request, error)

        def send_binary(data):
            self._client.send_binary(chr(stream_id) + data)

        def on_data(data):
            size = struct.unpack("ii", data)[1]
            if "file_object" in info:
                send_binary(info["file_object"].read(size))
            else:
                info["requested_size"] = size

        def on_close(close_request):
            if "file_object" in info:
                info["file_object"].close()
            else:
                info["stream_closed"] = True

            self._client.send_result(close_request, [])

        info = {}

        uid, stream_id = request["params"]

        self._data_store.get_filename(
            uid,
            reply_handler=get_filename_reply_handler,
            error_handler=error_handler)

        self._data_store.get_properties(
            uid, byte_arrays=True,
            reply_handler=get_properties_reply_handler,
            error_handler=error_handler)

        stream_monitor = self._client.stream_monitors[stream_id]
        stream_monitor.on_data = on_data
        stream_monitor.on_close = on_close

    def save(self, request):
        def reply_handler():
            self._client.send_result(info["close_request"], [])

        def error_handler(error):
            self._client.send_error(info["close_request"], error)

        def on_data(data):
            file_object.write(data[1:])

        def on_close(close_request):
            file_object.close()

            info["close_request"] = close_request
            self._data_store.update(uid, metadata, file_path, True,
                                    reply_handler=reply_handler,
                                    error_handler=error_handler)

        info = {}

        uid, metadata, stream_id = request["params"]

        file_path, file_object = self._create_file()

        stream_monitor = self._client.stream_monitors[stream_id]
        stream_monitor.on_data = on_data
        stream_monitor.on_close = on_close

        self._client.send_result(request, [])

    def create(self, request):
        def reply_handler(object_id):
            self._client.send_result(request, [object_id])

        def error_handler(error):
            self._client.send_error(request, error)

        self._data_store.create(request["params"][0], "", True,
                                reply_handler=reply_handler,
                                error_handler=error_handler)


class APIClient(object):
    def __init__(self, session):
        self._session = session

        self.activity_id = None
        self.stream_monitors = {}

    def send_result(self, request, result):
        response = {"result": result,
                    "error": None,
                    "id": request["id"]}

        self._session.send_message(json.dumps(response))

    def send_error(self, request, error):
        response = {"result": None,
                    "error": error,
                    "id": request["id"]}

        self._session.send_message(json.dumps(response))

    def send_notification(self, method, params=None):
        if params is None:
            params = []

        response = {"method": method,
                    "params": params}

        self._session.send_message(json.dumps(response))

    def send_binary(self, data):
        self._session.send_message(data, binary=True)


class APIServer(object):
    def __init__(self):
        self._stream_monitors = {}

        self._server = Server()
        self._server.connect("session-started", self._session_started_cb)
        self._port = self._server.start()
        self._key = os.urandom(16).encode("hex")

        self._apis = {}
        self._apis["activity"] = ActivityAPI
        self._apis["datastore"] = DatastoreAPI

    def setup_environment(self):
        os.environ["SUGAR_APISOCKET_PORT"] = str(self._port)
        os.environ["SUGAR_APISOCKET_KEY"] = self._key

    def _open_stream(self, client, request):
        for stream_id in xrange(0, 255):
            if stream_id not in client.stream_monitors:
                client.stream_monitors[stream_id] = StreamMonitor()
                break

        client.send_result(request, [stream_id])

    def _close_stream(self, client, request):
        stream_id = request["params"][0]
        stream_monitor = client.stream_monitors[stream_id]
        if stream_monitor.on_close:
            stream_monitor.on_close(request)

        del client.stream_monitors[stream_id]

    def _session_started_cb(self, server, session):
        session.connect("message-received",
                        self._message_received_cb, APIClient(session))

    def _message_received_cb(self, session, message, client):
        if message.message_type == Message.TYPE_BINARY:
            stream_id = ord(message.data[0])
            stream_monitor = client.stream_monitors[stream_id]
            stream_monitor.on_data(message.data)
            return

        request = json.loads(message.data)

        if request["method"] == "authenticate":
            params = request["params"]
            if self._key == params[1]:
                client.activity_id = params[0]
                return

        activity_id = client.activity_id
        if activity_id is None:
            return

        if request["method"] == "open_stream":
            self._open_stream(client, request)
        elif request["method"] == "close_stream":
            self._close_stream(client, request)
        else:
            api_name, method_name = request["method"].split(".")
            getattr(self._apis[api_name](client), method_name)(request)


def start():
    server = APIServer()
    server.setup_environment()
