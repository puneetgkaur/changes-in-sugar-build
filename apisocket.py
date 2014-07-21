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
import random

import base64
#import pygame

#import pygame.camera 
#from pygame.locals import *

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Wnck
from sugar3.graphics import style

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo
from gi.repository import GdkPixbuf

#from cordova.camera.record import Record

#from mediaview import MediaView
import cairo

from gi.repository import GdkX11


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


    def cordova_camera_show_object_chooser(self, request):
        chooser = ObjectChooser(self._activity, what_filter='Image')
        chooser.connect('response', self.cordova_camera_chooser_response_cb, request)
        chooser.show()

    def cordova_camera_chooser_response_cb(self, chooser, response_id, request):
        if response_id == Gtk.ResponseType.ACCEPT:
            object_id = chooser.get_selected_object_id()
            self._client.send_result(request, [object_id])
        else:
            self._client.send_result(request, [None])
        chooser.destroy()


    def camera(self,request):
        cam=camera_recorder(self._activity)
        cam.connect('response', self.cordova_camera_chooser_response_cb, request)
        cam.show()
        """
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
	pygame.camera.init()
        screen=pygame.display.set_mode((640,480),pygame.NOFRAME )
        pygame.display.set_caption("Click mouse/ press a key / close window to snap a photog")
    	camlist = pygame.camera.list_cameras()
    	if camlist:
            cam = pygame.camera.Camera(camlist[0],(640,480))
	cam.start()
        quit_loop=0
        base64data=None
        x=None
        data=None
        cam_image=cam.get_image()
        while quit_loop == 0:
	    cam_image=cam.get_image()
	    screen.blit(cam_image,(0,0))
	    pygame.display.update()
	    for event in pygame.event.get():
		if event.type == pygame.QUIT or  (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == MOUSEBUTTONDOWN):
		    #save the image
                    data = pygame.image.tostring(screen,"RGBA")
                    base64data = base64.b64encode(data)
                    #logging.error("base64 :\n %s",base64data)
		    #cam_image=cam.get_image()
		    cam.stop()
                    pygame.display.quit()
                    quit_loop=1
        logging.error("got base64 image")
        #logging.error("base64 :\n %s",base64data)
        pygame.image.save(cam_image,"/home/broot/Documents/image.jpg")
        #logging.error("josn dumps base64 :\n %s",json.dumps(base64data))
        self._client.send_result(request,base64data)
        """




    def conversionToBase64(self,request):
	CAMERA = '/home/broot/Documents/Photo by broot.jpe'
	fh = open(CAMERA)
	string = fh.read()
	fh.close()
        logging.error("reached camera function inside apisocket.py")        
        encoded_string = base64.b64encode(string)
	self._client.send_result(request,encoded_string)



    def accelerometer(self,request):
        logging.error("request : %s",request)
        timestamp = time.time()
        self._client.send_result(request,{'x':random.uniform(1, 10),'y':random.uniform(1, 10),'z':random.uniform(1, 10),'timestamp':timestamp,'keepCallback':True})


class camera_recorder(Gtk.Window):
    
    __gtype_name__ = 'camera_recorder'

    __gsignals__ = {
        'response': (GObject.SignalFlags.RUN_FIRST, None, ([int])),
    }
    
    def __init__(self, parent=None): 
        
        Gtk.Window.__init__(self)
        
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        #turn the following to false to avoid the gtk look
        self.set_decorated(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(style.LINE_WIDTH)
        self.set_has_resize_grip(False)
        
        self.add_events(Gdk.EventMask.VISIBILITY_NOTIFY_MASK)

        self.connect('button-press-event', self.__mouse_press_event_cb)
        
        if parent is None:
            logging.warning('Cordova camera: No parent window specified')
        else:
            self.connect('realize', self.__realize_cb, parent)

            screen = Wnck.Screen.get_default()
            screen.connect('window-closed', self.__window_closed_cb, parent)
        """
        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.show()
       
        self._toolbar = MainToolbox()
        self._toolbar.set_size_request(-1, style.GRID_CELL_SIZE)
        vbox.pack_start(self._toolbar, False, True, 0)
        self._toolbar.show()
        """
        
        self.width = Gdk.Screen.width() - style.GRID_CELL_SIZE * 2
        self.height = Gdk.Screen.height() - style.GRID_CELL_SIZE * 2
        self.set_size_request(self.width, self.height)


        self.movie_window = Gtk.DrawingArea()
        self.add(self.movie_window)  

        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)
               

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)


        # Create GStreamer elements
        self.src = Gst.ElementFactory.make('autovideosrc', None)
        self.sink = Gst.ElementFactory.make('xvimagesink', None)

        # Add elements to the pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.sink)

        """
        self.filesink = Gst.ElementFactory.make("filesink", None)
        self.filesink.set_property("location", "/home/broot/sugar-build/test.jpeg")
        self.pipeline.add(self.filesink)
        """

        self.src.link(self.sink)

        self.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.movie_window.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        


    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            logging.error('prepare-window-handle')
            #msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle( self.xid)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())

    def __realize_cb(self, chooser, parent):
        logging.error("hello")
        #self.get_window().set_transient_for(parent)    

    def __window_closed_cb(self, screen, window, parent):
        if window.get_xid() == parent.get_xid():
            self.destroy()

    def __mouse_press_event_cb(self, widget, event):
        self.pipeline.set_state(Gst.State.PAUSED)
        #root_win = Gdk.get_default_root_window()
        gdk_window = Gdk.get_default_root_window()

        #gdk_display = GdkX11.X11Display.get_default()
        #gdk_window = GdkX11.X11Window.foreign_new_for_display(gdk_display,self.xid)

        

        width = gdk_window.get_width()
        height = gdk_window.get_height()    
    
        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)                
        pb = Gdk.pixbuf_get_from_window(gdk_window, 0, 0, width, height)
        
        cr = cairo.Context(ims)    
        Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)     
        cr.paint()

        ims.write_to_png('/home/broot/sugar-build/testimage'+self.snapshot_name()+'.png')


        """
        #root_window = Gdk.get_default_root_window()
        self.pipeline.set_state(Gst.State.PAUSED)
        pix = Gdk.pixbuf_get_from_window(self.get_window(),0, 0,self.get_window().get_width(),self.get_window().get_height())

        pix.savev('/home/broot/sugar-build/testimage.jpeg', 'jpeg', [], [])

        ############
        drawable = self.movie_window.get_window()
        logging.error("drawable: %s : ",drawable)
        
        # Fetch what we rendered on the drawing area into a pixbuf
        pixbuf = Gdk.pixbuf_get_from_window(drawable,0,0,self.width,self.height)
        
        # Write the pixbuf as a PNG image to disk
        pixbuf.savev('/home/broot/sugar-build/testimage.jpeg', 'jpeg', [], [])
        ############
        colormap = drawable.get_colormap()
        pixbuf = Gtk.Gdk.Pixbuf(Gtk.Gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0,0,0,0, *drawable.get_size()) 
        pixbuf = pixbuf.scale_simple(self.width, self.height, Gtk.Gdk.INTERP_HYPER) # resize
        # We resize from actual window size to wanted resolution
        # gtk.gdk.INTER_HYPER is the slowest and highest quality reconstruction function
        # More info here : http://developer.gnome.org/pygtk/stable/class-gdkpixbuf.html#method-gdkpixbuf--scale-simple
        filename = self.snapshot_name() + '.jpeg'
        filepath = relpath(filename)
        pixbuf.save('/home/broot/sugar-build/testimage.jpeg', 'jpeg')
        #return filepath
        """
        self.pipeline.set_state(Gst.State.NULL)
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)

    def snapshot_name(self):
        """ Return a string of the form yyyy-mm-dd-hms """
        from datetime import datetime
        today = datetime.today()
        y = str(today.year)
        m = str(today.month)
        d = str(today.day)
        h = str(today.hour)
        mi= str(today.minute)
        s = str(today.second)
        return '%s-%s-%s-%s%s%s' %(y, m, d, h, mi, s)


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
