import os, wx, fitz, PyPDF2
from time import strftime
from shutil import copy

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
        self.fileSelectButton = wx.Button(self.buttonPanel, label="Select a file")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.fileSelectButton)
        # Page rotate left button
        self.rotateLeftButton = wx.Button(self.buttonPanel, label="Rotate Left")
        self.Bind(wx.EVT_BUTTON, self.OnRotateLeft, self.rotateLeftButton)
        # Page rotate right button
        self.rotateRightButton = wx.Button(self.buttonPanel, label="Rotate Right")
        self.Bind(wx.EVT_BUTTON, self.OnRotateRight, self.rotateRightButton)
        # Save button
        self.saveButton = wx.Button(self.buttonPanel, label="Save")
        self.Bind(wx.EVT_BUTTON, self.Save, self.saveButton)

        # buttonPanel sizer
        self.buttonPanelSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonPanelSizer.Add(self.fileSelectButton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.buttonPanelSizer.Add(self.rotateLeftButton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.buttonPanelSizer.Add(self.rotateRightButton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.buttonPanelSizer.Add(self.saveButton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.buttonPanel.SetSizerAndFit(self.buttonPanelSizer)

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

            # copy PDF file to temp file
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.absPath = os.path.join(self.dirname, self.filename)
            self.tempAbsPath = os.path.join(self.tempDir, self.filename)
            copy(self.absPath, self.tempAbsPath)

            # load temp file
            doc = fitz.Document(self.tempAbsPath)
            self.numPages = doc.pageCount
            self.docImages = [];
            tempPdfFile = open(self.tempAbsPath, 'rb')
            self.pdfReader = PyPDF2.PdfFileReader(tempPdfFile)

            # create images from all pages and get page objects
            for i in xrange(self.numPages):
                pgpix = doc.loadPage(i).getPixmap()
                self.docImages.append(wx.BitmapFromBufferRGBA(
                    pgpix.width, pgpix.height, pgpix.samples
                ).ConvertToImage())

            # close doc
            doc.close()

            # get first page and display
            self.DisplayPage(0)
            self.currPage = 0;

        dlg.Destroy()

    def DisplayPage(self, pgIndex):
        """Displays the given page on the screen, scaled to fit width of window."""

        # get page and scale image to fill width of panel
        pg = self.docImages[pgIndex]
        newWidth = self.displayPanel.GetClientSize().GetWidth()
        newHeight = pg.GetHeight() / (pg.GetWidth() / float(newWidth))
        pg = pg.Scale(newWidth, newHeight)

        # Change the displayed image
        self.imageDisplay.SetBitmap(wx.BitmapFromImage(pg))
        self.Refresh()

    def OnBackButton(self, e):
        if self.currPage != 0:
            self.currPage -= 1
            self.DisplayPage(self.currPage)

    def OnNextButton(self, e):
        if self.currPage != self.numPages-1:
            self.currPage += 1
            self.DisplayPage(self.currPage)

    def OnRotateLeft(self, e):
        """Rotates the shown page counterclockwise 90 degrees."""
        # Rotate the image
        self.docImages[self.currPage] = self.docImages[self.currPage].Rotate90(False)

        # Rotate the PDF page
        self.pdfReader.getPage(self.currPage).rotateCounterClockwise(90)

        self.DisplayPage(self.currPage)

    def OnRotateRight(self, e):
        """Rotates the shown page clockwise 90 degrees."""
        # Rotate the image
        self.docImages[self.currPage] = self.docImages[self.currPage].Rotate90(True)

        # Rotate the PDF page
        self.pdfReader.getPage(self.currPage).rotateClockwise(90)

        self.DisplayPage(self.currPage)

    def Save(self, e):
        """Saves the PDF file."""
        pdfOutput = open(self.absPath, 'wb')
        pdfWriter = PyPDF2.PdfFileWriter()

        pdfWriter.appendPagesFromReader(self.pdfReader)

        pdfWriter.write(pdfOutput)
        pdfOutput.close()


app = wx.App(False)
frame = EditorWindow(title="PDFEditor", size=(500,500))
frame.Show()
app.MainLoop()
