import os
import wx
import fitz
from time import strftime

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
        self.pageNavPanel = wx.Panel(self.mainPanel)
        #self.displayPanel.SetScrollbar(wx.VERTICAL, 0, 5, 10)

        # File selector button
        self.button = wx.Button(self.buttonPanel, label="Select a file")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.button)
        # Page rotate left button
        self.rotateLeftButton = wx.Button(self.buttonPanel, label="Rotate Left")
        #self.Bind(wx.EVT_BUTTON, self.OnRotateLeft, self.rotateLeftButton)
        # Page rotate right button
        self.rotateRightButton = wx.Button(self.buttonPanel, label="Rotate Right")
        #self.Bind(wx.EVT_BUTTON, self.OnRotateRight, self.rotateRightButton)

        # PDF image
        self.imageDisplay = wx.StaticBitmap(self.displayPanel, wx.ID_ANY)

        # PDF page navigation buttons
        self.backButton = wx.Button(self.pageNavPanel, label="<")
        self.Bind(wx.EVT_BUTTON, self.OnBackButton, self.backButton)
        self.nextButton = wx.Button(self.pageNavPanel, label=">")
        self.Bind(wx.EVT_BUTTON, self.OnNextButton, self.nextButton)
        self.pageNavSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pageNavSizer.Add(self.backButton, 0, wx.ALL, 5)
        self.pageNavSizer.Add(self.nextButton, 0, wx.ALL, 5)
        self.pageNavPanel.SetSizerAndFit(self.pageNavSizer)

        # Place elements in display sizer
        self.displaySizer = wx.BoxSizer(wx.VERTICAL)
        self.displaySizer.Add(self.displayPanel, 5, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.displaySizer.Add(self.pageNavPanel, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Place all elements in the main sizer
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.buttonPanel, 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(self.displaySizer, 5, wx.ALL|wx.EXPAND, 5)

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
            self.tempname = strftime("%Y%m%d%H%M%S")
            absPath = os.path.join(self.dirname, self.filename)
            doc = fitz.Document(absPath)
            self.numPages = doc.pageCount
            self.docImages = [];

            # create images from all pages
            for i in xrange(self.numPages):
                pgpix = doc.loadPage(i).getPixmap()
                self.docImages.append(wx.BitmapFromBufferRGBA(
                    pgpix.width, pgpix.height, pgpix.samples
                ).ConvertToImage())

            # get first page and scale image to fill width of panel
            self.DisplayPage(1)
            self.currPage = 1;

        dlg.Destroy()

    def DisplayPage(self, pgNum):
        """Displays the given page on the screen"""

        # get page and scale image to fill width of panel
        pg = self.docImages[pgNum-1]
        newWidth = self.displayPanel.GetClientSize().GetWidth()
        newHeight = pg.GetHeight() / (pg.GetWidth() / float(newWidth))
        pg = pg.Scale(newWidth, newHeight)

        # Change the displayed image
        self.imageDisplay.SetBitmap(wx.BitmapFromImage(pg))
        self.Refresh()

    def OnBackButton(self, e):
        if self.currPage != 1:
            self.currPage -= 1
            self.DisplayPage(self.currPage)

    def OnNextButton(self, e):
        if self.currPage != self.numPages:
            self.currPage += 1
            self.DisplayPage(self.currPage)

    #def OnRotateLeft(self, e):


app = wx.App(False)
frame = EditorWindow(title="PDFEditor", size=(500,500))
frame.Show()
app.MainLoop()
