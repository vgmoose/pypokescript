import wx, wx.html2, wx.lib, wx.lib.newevent

from flask import Flask
from threading import Thread, Lock

from pypokescript.games.utils.nds import NDS
from pypokescript.games.utils.narc import NARC

# only supported target right now
from pypokescript.games.b2w2 import b2w2

import pypokescript as ps

class Container:
    pass

g = Container()

PORT = 8073
BrowseEvent, BROWSE_EVENT = wx.lib.newevent.NewEvent()

DEVELOPMENT = False

if not DEVELOPMENT:
    import pypokescript.gui     # import self to get path later
    import os

def composePage(target, notice=None, data={}):
    p = ""
    if not DEVELOPMENT:
        p = os.path.dirname(pypokescript.gui.__file__) + os.sep
    # compose the desired page from different UI components
    resp = ""

    # if there's data, create a js object and insert it into the page
    if data:
        resp += "<script> data = %s; </script>" % str(data);

    resp += open(p + "header.html", "r").read()
    if notice:
        resp += "<div class='notice'>%s</div>" % notice
    resp += "<style>" + open(p + "index.css", "r").read() + "</style>"
    resp += open(p + target+".html", "r").read()

    return resp

class MyBrowser(wx.Dialog):
    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.SetSize((700, 700))
        self.selectedFile = None

        self.lock = Lock()

    def showFileBrowser(self):
        dialog = wx.FileDialog(
        self, "Choose the ROM to edit", "", "nds", "NDS Files (*.nds)|*.nds", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.selectedFile = dialog.GetPath()
        else:
            self.selectedFile = None
        dialog.Destroy()

        # release Lock
        self.lock.release()

    def browseForFile(self, arg):
        self.showFileBrowser()

def start_flask(dialog):
    flask_app = Flask(__name__)

    @flask_app.route("/")
    def main():
        return composePage("main")

    @flask_app.route("/scripts/<number>")
    def get_script(number):
        # get the script for the current number, from the currently
        # loaded script NARC file (TODO: break apart for other targets)
        return ps.PokeScript(g.narc.files[int(number)], isPath=False).getText()

    @flask_app.route("/open", methods=["POST"])
    def open():
        # show dialog by signaling the main app loop
        evt = BrowseEvent()
        dialog.lock.acquire()
        wx.PostEvent(dialog, evt)

        dialog.lock.acquire(blocking=True)
        dialog.lock.release()

        if (dialog.selectedFile):
            # open NDS file
            g.nds = NDS(dialog.selectedFile)
            g.narc = NARC(g.nds, b2w2.SCRIPT_PATH)

            data = {"count": len(g.narc.files)}
            resp = composePage("editor", None, data)

            return resp
        else:
            return composePage("main", notice="Please select a file")

    flask_app.run(port=PORT)

if __name__ == '__main__':

    # start flask in a background thread, it's going to respond to requests
    # from wx
    wx_app = wx.App()

    # bind
    dialog = MyBrowser(None, -1)
    dialog.Bind(BROWSE_EVENT, dialog.browseForFile)

    t = Thread(target=start_flask, args=(dialog,))
    t.start()

    # dialog.showDialog()
    dialog.browser.LoadURL("http://127.0.0.1:%d" % PORT)
    dialog.ShowModal()
    wx_app.MainLoop()
