import os
from gi.repository import Gtk
from gi.repository import GdkX11
import base64
import pygame

import pygame.camera 
from pygame.locals import *

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
import cairo

from jarabe.journal.objectchooser import ObjectChooser

import logging

def webcam_display(parent_activity):
    cam=camera_recorder(parent_activity)
    cam.connect('response', chooser_response_cb)
    cam.show()


def chooser_response_cb(chooser, response_id):
    if response_id == Gtk.ResponseType.ACCEPT:
        object_id = chooser.get_selected_object_id()
        chooser.destroy()
        logging.error(object_id)
        return object_id
    else:
        chooser.destroy()
        return None
    

def show_image_chooser(parent):
    chooser = ObjectChooser(parent._activity, what_filter='Image')
    chooser.connect('response', chooser_response_cb)
    chooser.show()

def conversionToBase64():
    CAMERA = '/home/broot/Documents/Photo by broot.jpe'
    fh = open(CAMERA)
    string = fh.read()
    fh.close()
    logging.error("reached camera function inside apisocket.py")        
    encoded_string = base64.b64encode(string)
    return encoded_string



class pygame_camera:
    def __init__(self,parent=None):
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
                    #logging.error("base64 :\n %s",base64data)cam_image=cam.get_image()
                    cam.stop()
                    pygame.display.quit()
                    quit_loop=1
        logging.error("got base64 image")
        #logging.error("base64 :\n %s",base64data)
        pygame.image.save(cam_image,"/home/broot/Documents/image.jpg")
        #logging.error("josn dumps base64 :\n %s",json.dumps(base64data))
        self._client.send_result(request,base64data)


class camera_recorder(Gtk.Window):
    
    __gtype_name__ = 'camera_recorder'

    __gsignals__ = {
        'response': (GObject.SignalFlags.RUN_FIRST, None, ([int])),
    }
    
    def __init__(self,parent=None): 
        
        Gtk.Window.__init__(self)
        self.activity=parent
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

        
        ########
        """
        self.filesink = Gst.ElementFactory.make("filesink", None)
        self.filesink.set_property("location", "/home/broot/sugar-build/test.jpeg")
        self.pipeline.add(self.filesink)
        """
        ########
        

        self.src.link(self.sink)

        self.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.movie_window.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        """
        self.glive = Glive(self.activity,parent_obj)
        pad = self.glive._photobin.get_static_pad("sink")
        self.glive._pipeline.add(self.glive._photobin)
        self.glive._photobin.set_state(Gst.STATE_PLAYING)
        self.glive._pipeline.get_by_name("tee").link(self.glive._photobin)        
        """

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
        #self.glive.take_photo()
        """
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
        """
        ############

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


