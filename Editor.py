import os
import wx
import fitz

class EditorWindow(wx.Frame):
    def __init__(self, **kwargs):
        wx.Frame.__init__(self, None, **kwargs)

        # Create temp directory if it doesn't exist
        self.tempDir = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(self.tempDir):
            os.mkdir(self.tempDir)

        # Panels
        self.mainPanel = wx.Panel(self)
        self.buttonPanel = wx.Panel(self.mainPanel)
        self.displayPanel = wx.Panel(self.mainPanel, style=wx.SUNKEN_BORDER)
        #self.displayPanel.SetScrollbar(wx.VERTICAL, 0, 5, 10)

        # File selector button
        self.button = wx.Button(self.buttonPanel, label="Select a file")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.button)

        # PDF image
        self.imageDisplay = wx.StaticBitmap(self.displayPanel, wx.ID_ANY)

        # Place all elements in the main sizer
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.buttonPanel, 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(self.displayPanel, 5, wx.ALL|wx.EXPAND, 5)

        self.mainPanel.SetSizerAndFit(self.mainSizer)

    def OnOpen(self, e):
        """Opens a file."""
        self.dirname = ''
        filetypes = "PDF Files (*.pdf)|*.pdf"
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", filetypes, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:

            # load PDF file
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            absPath = os.path.join(self.dirname, self.filename)
            doc = fitz.Document(absPath)
            #image = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)

            # get first page
            page = doc.loadPage(0)
            pixmap = page.getPixmap()
            pg1AbsPath = os.path.join(self.tempDir,self.filename+"pg1.png")
            pixmap.writePNG(pg1AbsPath)
            image = wx.Image(pg1AbsPath, wx.BITMAP_TYPE_ANY)

            # scale image
            newWidth = self.displayPanel.GetClientSize().GetWidth()
            newHeight = image.GetHeight() / (image.GetWidth() / float(newWidth))
            image = image.Scale(newWidth, newHeight)

            # Change the displayed image
            self.imageDisplay.SetBitmap(wx.BitmapFromImage(image))
            self.Refresh()
        dlg.Destroy()

app = wx.App(False)
frame = EditorWindow(title="PDFEditor", size=(500,500))
frame.Show()
app.MainLoop()
