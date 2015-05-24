__author__ = 'corona'

import os
import sys
import xbmcgui
from selenium.webdriver.common.keys import Keys
import xbmc
sleep = xbmc.sleep

import send_keys

DEFAULT_KEYMAP = {
    xbmcgui.ACTION_SELECT_ITEM   : ("sendkey",Keys.SPACE),
    xbmcgui.ACTION_MOVE_LEFT     : ("sendkey",Keys.ARROW_LEFT),
    xbmcgui.ACTION_MOVE_RIGHT    : ("sendkey",Keys.ARROW_RIGHT),
    xbmcgui.ACTION_MOVE_UP       : ("sendkey",Keys.ARROW_UP),
    xbmcgui.ACTION_MOVE_DOWN     : ("sendkey",Keys.ARROW_DOWN),
    xbmcgui.ACTION_PLAY          : ("sendkey",Keys.SPACE),
    xbmcgui.ACTION_NAV_BACK      : ("exit",None),
    xbmcgui.ACTION_PARENT_DIR    : ("exit",None),
    xbmcgui.ACTION_PREVIOUS_MENU : ("exit",None),
    xbmcgui.ACTION_STOP          : ("exit",None),
    xbmcgui.ACTION_SHOW_INFO     : ("exit",None),
    xbmcgui.ACTION_SHOW_GUI      : ("exit",None),
}

# KEY_ACTION_MAP = {
#     "Esc"    : xbmcgui.ACTION_PREVIOUS_MENU,
#     "Up"     : xbmcgui.ACTION_MOVE_UP,
#     "Down"   : xbmcgui.ACTION_MOVE_DOWN,
#     "Left"   : xbmcgui.ACTION_MOVE_LEFT,
#     "Right"  : xbmcgui.ACTION_MOVE_RIGHT,
#     "P"      : xbmcgui.ACTION_PLAY,
# }

class WindowXMLDialogActions(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback=0, parent = None):
        self.parent = parent
        xbmcgui.WindowXMLDialog.__init__( self )

    def onAction(self, *args):
        if self.parent:
            self.parent.onAction(*args)

class window(object):
    def __init__(self, browser, jsTarget):
        chromedriver_plugin_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..',))
        self.window = WindowXMLDialogActions('window.xml', chromedriver_plugin_folder, 'default', parent=self)
        self.browser = browser
        self.jsTarget = jsTarget
        self.keymap = DEFAULT_KEYMAP

    def _backgroundJsHandler(self, stopEvt):
        """
        Runs in thread while control window is open
        """
        self.browser.startMonitoringKeystrokes()
        sender = send_keys.KeySender()
        while not stopEvt.is_set():
            keys = self.browser.getKeystrokes()
#            for key in keys:
            if keys:
                sender.send_key(keys)
 #               action = KEY_ACTION_MAP.get(key.get('name', None), None)
  #              if action:
   #                 self.onAction(action)
                sleep(25)
            else:
                sleep(250)

    def doModal(self):
        import threading
        stopEvt = threading.Event()
        try:
            thread = threading.Thread(target = self._backgroundJsHandler, args=(stopEvt,))
            thread.daemon = True
            thread.start()
            self.window.doModal()
        finally:
            stopEvt.set()

    def setKeymapCallback(self, keymap):
        self.keymap = keymap if keymap is not None else DEFAULT_KEYMAP

    def onAction(self, action):
        action = action.getId() if isinstance(action, xbmcgui.Action) else action
        action_name, args = self.keymap.get(action, (None, None))
        if action_name:
            self.__getattribute__("action_"+str(action_name))(args)

    def action_exit(self,*args):
        self.window.close()

    def action_sendkey(self,*args):
        self.browser.send_keys(*args+(self.jsTarget,))
