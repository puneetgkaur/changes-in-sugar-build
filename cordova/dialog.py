# Copyright (C) 2007, One Laptop Per Child
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

from gettext import gettext as _
import logging

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Wnck

from sugar3.graphics import style
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.objectchooser import FILTER_TYPE_MIME_BY_ACTIVITY

from jarabe.journal.listview import BaseListView
from jarabe.journal.listmodel import ListModel
from jarabe.journal.journaltoolbox import MainToolbox
from jarabe.journal.volumestoolbar import VolumesToolbar
from jarabe.model import bundleregistry

from jarabe.journal.iconview import IconView


def dialog_response(dialog_box, response_id):
    dialog_box.destroy()
    return None

def show_dialog(parent):
    dialog = dialog_window(parent)
    dialog.connect('response', dialog_response)
    dialog.show()

class dialog_window(Gtk.Window):
    
    __gtype_name__ = 'dialog_window'

    __gsignals__ = {
        'response': (GObject.SignalFlags.RUN_FIRST, None, ([int])),
    }
    
    def __init__(self,parent=None): 
        
        Gtk.Window.__init__(self)
        self.activity=parent
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_decorated(False)
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
        
        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.show()

        title_box = TitleBox()
        title_box.close_button.connect('clicked',
                                       self.__close_button_clicked_cb)
        title_box.set_size_request(-1, style.GRID_CELL_SIZE)
        vbox.pack_start(title_box, False, True, 0)
        title_box.show()

        self.width = Gdk.Screen.width() - style.GRID_CELL_SIZE * 2
        self.height = Gdk.Screen.height() - style.GRID_CELL_SIZE * 2
        self.set_size_request(self.width, self.height)

        self.show_all()


    def __realize_cb(self, chooser, parent):
        logging.error("hello")
        self.get_window().set_transient_for(parent)    

    def __window_closed_cb(self, screen, window, parent):
        if window.get_xid() == parent.get_xid():
            self.destroy()

    def __delete_event_cb(self, chooser, event):
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)


    def __mouse_press_event_cb(self, widget, event):
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)
      
    def __close_button_clicked_cb(self, button):
        self.emit('response', Gtk.ResponseType.DELETE_EVENT)


class TitleBox(Gtk.Toolbar):

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        label = Gtk.Label()
        title = _('Choose an object')

        label.set_markup('<b>%s</b>' % title)
        label.set_alignment(0, 0.5)
        self._add_widget(label, expand=True)

        self.close_button = ToolButton(icon_name='dialog-cancel')
        self.close_button.set_tooltip(_('Close'))
        self.insert(self.close_button, -1)
        self.close_button.show()

    def _add_widget(self, widget, expand=False):
        tool_item = Gtk.ToolItem()
        tool_item.set_expand(expand)

        tool_item.add(widget)
        widget.show()

        self.insert(tool_item, -1)
        tool_item.show()
