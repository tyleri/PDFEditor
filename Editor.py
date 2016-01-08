import os
import wx

class EditorWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.button = wx.Button(self, label="Select a file")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.button)

    def OnOpen(self, e):
        """Opens a file."""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.control.SetValue(f.read())
            print f.read()
            f.close()
        dlg.Destroy()

app = wx.App(False)
frame = wx.Frame(None)
panel = EditorWindow(frame)
frame.Show()
app.MainLoop()
