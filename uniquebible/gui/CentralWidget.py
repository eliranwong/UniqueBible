from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QGridLayout, QWidget, QSplitter
else:
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QGridLayout, QWidget, QSplitter
from uniquebible.gui.TabWidget import TabWidget
from uniquebible.gui.WebEngineView import WebEngineView


class CentralWidget(QWidget):

    instantRatio = {
        0: (2, 0),
        1: (10, 1),
        2: (5, 2),
        3: (2, 2),
    }

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        #self.html = "<h1>UniqueBible.app</h1><p>This is '<b>Main View</b>'.</p>"

        #self.mainView = WebEngineView(self, "main")
        #self.mainView.setHtml(self.html, baseUrl)
        #self.studyView = WebEngineView(self, "study")
        #self.studyView.setHtml("This is '<b>Study View</b>'.", baseUrl)
        
        self.instantSplitter = QSplitter(Qt.Vertical, parent)
      
        if config.landscapeMode:            
            self.parallelSplitter = QSplitter(Qt.Horizontal)
        else:
            self.parallelSplitter = QSplitter(Qt.Vertical)

        self.mainView = TabWidget(self, "main")
        self.parent.mainView = self.mainView
        for i in range(config.numberOfTab):
            tabView = WebEngineView(self, "main")
            self.mainView.addTab(tabView, "{1}{0}".format(i+1, config.thisTranslation["tabBible"]))
            tabView.titleChanged.connect(self.parent.mainTextCommandChanged)
            tabView.loadStarted.connect(self.parent.startLoading)
            tabView.loadFinished.connect(lambda ok, index=i: self.parent.finishMainViewLoading(ok, index=index))
            #tabView.renderProcessTerminated.connect(self.parent.checkMainPageTermination)
            tabView.page().pdfPrintingFinished.connect(self.parent.pdfPrintingFinishedAction)

        self.studyView = TabWidget(self, "study")
        self.parent.studyView = self.studyView
        for i in range(config.numberOfTab):
            tabView = WebEngineView(self, "study")
            self.studyView.addTab(tabView, "{1}{0}".format(i+1, config.thisTranslation["tabStudy"]))
            tabView.titleChanged.connect(self.parent.studyTextCommandChanged)
            tabView.loadStarted.connect(self.parent.startLoading)
            tabView.loadFinished.connect(lambda ok, index=i: self.parent.finishStudyViewLoading(ok, index=index))
            #tabView.renderProcessTerminated.connect(self.parent.checkStudyPageTermination)
            tabView.page().pdfPrintingFinished.connect(self.parent.pdfPrintingFinishedAction)

        self.instantView = WebEngineView(self, "instant")
        self.instantView.setHtml("<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{1}.css?v=1.065'><link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.065'><p style='font-family:{0};'><u><b>Bottom Window</b></u><br>Display instant information on this window by hovering over verse numbers, tagged words or bible reference links.</p>".format(config.font, config.theme), config.baseUrl)

        self.parallelSplitter.addWidget(self.mainView)
        self.parallelSplitter.addWidget(self.studyView)
        
        self.parallelSplitter.setHandleWidth(5)
        self.instantSplitter.setHandleWidth(5)

        self.instantSplitter.addWidget(self.parallelSplitter)
        self.instantSplitter.addWidget(self.instantView)

        # Adding signals
        self.instantSplitter.splitterMoved.connect(self.onInstantSplitterMoved)
        self.parallelSplitter.splitterMoved.connect(self.onParallelSplitterMoved)

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 10, 0, 3)
        # self.layout.setHorizontalSpacing(0)
        # self.layout.setVerticalSpacing(2)        
        self.layout.addWidget(self.instantSplitter)                
        
        self.setLayout(self.layout)

        # Popup windows
        self.popoverView = None
        self.popoverUrlView = None

    def onInstantSplitterMoved(self, pos, index):      
        config.instantMode = -1
        config.iModeSplitterSizes = self.instantSplitter.sizes()

    def onParallelSplitterMoved(self, pos, index):
        config.parallelMode = -1
        config.pModeSplitterSizes = self.parallelSplitter.sizes()

    def switchLandscapeMode(self):
        if config.landscapeMode:
            # Switch to Landscape
            self.parallelSplitter.setOrientation(Qt.Horizontal)
        else:
            #Switch to Portrait
            self.parallelSplitter.setOrientation(Qt.Vertical)

    def resizeMe(self):        
        if config.landscapeMode:
            self.resizeAsLandscape()
        else:
            self.resizeAsPortrait()        

    def resizeAsLandscape(self):
        parallelRatio = {
            0: (1, 0),
            1: (2, 1),
            2: (1, 1),
            3: (1, 2),
            4: (0, 1),
        }

        # The total space we have.
        w, h = (self.parallelSplitter.width(), self.instantSplitter.height())

        if config.parallelMode == -1:                        
            left, right = config.pModeSplitterSizes
            w = left + right
        else:
            left, right = parallelRatio[config.parallelMode]
            
        self.parallelSplitter.setSizes([w * left // (left+right), w * right // (left+right)])
       
        if config.parallelMode:
            self.studyView.show()
        else:
            self.studyView.hide()

        if config.instantMode == -1:
            top, bottom = config.iModeSplitterSizes
            h = top + bottom
        else:
            top, bottom = CentralWidget.instantRatio[config.instantMode]

        self.instantSplitter.setSizes([h * top // (top + bottom), h * bottom // (top + bottom)])
        
        if config.instantMode:
            self.instantView.show()
        else:
            self.instantView.hide()

    def resizeAsPortrait(self):

        parallelRatio = {
            (0,  0): (10, 0, 0),
            (0,  1): (10, 5, 0),
            (0,  2): (5, 5, 0),
            (0,  3): (5, 10, 0),
            (0,  4): (0, 10, 0),
            (1,  0): (10, 0, 1),            
            (1,  1): (20, 10, 3),
            (1,  2): (5, 5, 1),
            (1,  3): (10, 20, 3),
            (1,  4): (0, 10, 1),
            (2,  0): (10, 0, 4),
            (2,  1): (10, 5, 6),
            (2,  2): (5, 5, 4),
            (2,  3): (5, 10, 6),
            (2,  4): (0, 10, 4),
            (3,  0): (10, 0, 10),
            (3,  1): (10, 5, 15),
            (3,  2): (10, 10, 20),
            (3,  3): (5, 10, 15),
            (3,  4): (0, 10, 10),
        }      

        h = self.instantSplitter.height()

        if config.instantMode == -1:
            i1, i2 = config.iModeSplitterSizes
            h = i1 + i2
            bottom = i2 * h // (i1 + i2)
            remaining = h - bottom

            if config.parallelMode == -1:
                s1, s2 = config.pModeSplitterSizes
                top = s1 * remaining // (s1 + s2)
                middle = s2 * remaining // (s1 + s2)

            else: # i.e. config.parallelMode is not custom
                _top, _middle, _bottom = parallelRatio[(0, config.parallelMode)]
                top = _top * remaining // (_top + _middle)
                middle = _middle * remaining // (_top + _middle)

        else: # i.e. config.instantMode is set

            if config.parallelMode == -1:
                s1, s2 = config.pModeSplitterSizes
                _top, _middle, _bottom = parallelRatio[(config.instantMode, 0)]

                bottom = h * _bottom // (_top + _middle + _bottom)
                remaining = h - bottom

                top = s1 * remaining // (s1 + s2)
                middle = s2 * remaining // (s1 + s2)

            else:
                _top, _middle, _bottom = parallelRatio[(config.instantMode, config.parallelMode)]
                top = h * _top // (_top + _middle + _bottom)
                middle = h * _middle // (_top + _middle + _bottom)
                bottom = h * _bottom // (_top + _middle + _bottom)

        self.instantSplitter.setSizes([top + middle, bottom])
        self.parallelSplitter.setSizes([top, middle])
   
        if config.parallelMode:
            self.studyView.show()
        else:
            self.studyView.hide()
        
        if config.instantMode:
            self.instantView.show()
        else:
            self.instantView.hide()
