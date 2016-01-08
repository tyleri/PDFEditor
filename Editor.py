import os
import wx

class EditorWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.button = wx.Button(self, label="Select a file")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.button)

        img = wx.EmptyImage(500, 500)
        self.imageDisplay = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(img))

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.button, 0, wx.ALL, 5)
        self.mainSizer.Add(self.imageDisplay, 0, wx.ALL, 5)

        self.SetSizerAndFit(self.mainSizer)

    def OnOpen(self, e):
        """Opens a file."""
        self.dirname = ''
        filetypes = "Pictures (*.jpg;*.jpeg;*.png)|*.jpg;*.jpeg;*.png"
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", filetypes, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            imageFile = os.path.join(self.dirname, self.filename)
            image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)

            # scale image
            maxSize = 500
            width = image.GetWidth()
            height = image.GetHeight()

            if width > maxSize or height > maxSize:
                if width > height:
                    newWidth = 500
                    newHeight = height / (width / 500.0)
                else:
                    newHeight = 500
                    newWidth = width / (height / 500.0)

                image = image.Scale(newWidth, newHeight)

            # Change the displayed image
            self.imageDisplay.SetBitmap(wx.BitmapFromImage(image))
            self.Refresh()
        dlg.Destroy()

app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "PDFEditor", (0,0), (600,600))
panel = EditorWindow(frame)
frame.Show()
app.MainLoop()
