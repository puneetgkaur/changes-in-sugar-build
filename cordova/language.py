
import locale
import gettext
from gi.repository import Gio
from jarabe import config
import os
import logging
import subprocess

"""
def setup_locale():
    
    # NOTE: This needs to happen early because some modules register
    # translatable strings in the module scope.
    gettext.bindtextdomain('sugar', config.locale_path)
    gettext.bindtextdomain('sugar-toolkit-gtk3', config.locale_path)
    gettext.textdomain('sugar')

    settings = Gio.Settings('org.sugarlabs.date')
    timezone = settings.get_string('timezone')
    if timezone is not None and timezone:
        os.environ['TZ'] = timezone
   
""" 

def get_locale_name():
    
    #setup_locale()
    logging.error(os.environ.get('HOME'))
    path = os.path.join(os.environ.get('HOME'), '.i18n')
    fd = open(path)
    str_language_file=fd.read()
    fd.close()
    logging.error("On reading language file : %s",str_language_file)
    _default_lang = '%s.%s' % locale.getdefaultlocale()
    logging.error("default language : %s",_default_lang)    
    
    return _default_lang


def get_perferred_language():
    return "English"


