import config
from ast import literal_eval
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QGridLayout, QWidget)
from PySide2.QtWidgets import QSplitter
from translations import translations
from gui.TabWidget import TabWidget
from gui.WebEngineView import WebEngineView

class CentralWidget(QWidget):

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

        self.studyView = TabWidget(self, "study")
        self.parent.studyView = self.studyView
        for i in range(config.numberOfTab):
            tabView = WebEngineView(self, "study")
            self.studyView.addTab(tabView, "{1}{0}".format(i+1, config.thisTranslation["tabStudy"]))

        self.instantView = WebEngineView(self, "instant")
        self.instantView.setHtml("<link rel='stylesheet' type='text/css' href='css/{1}.css'><p style='font-family:{0};'><u><b>Bottom Window</b></u><br>Display instant information on this window by hovering over verse numbers, tagged words or bible reference links.</p>".format(config.font, config.theme), config.baseUrl)

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
        }

        # The total space we have.
        w, h = [ self.parallelSplitter.width(), self.instantSplitter.height() ]

        if config.parallelMode == -1:                        
            left, right = config.pModeSplitterSizes
            w = left + right
        else:
            left, right = parallelRatio[config.parallelMode]
            
        self.parallelSplitter.setSizes([ w * left // (left+right), w * right // (left+right)])
       
        if config.parallelMode:
            self.studyView.show()
        else:
            self.studyView.hide()

        # Then resize instantView
        instantRatio = {
            0: (2, 0),
            1: (5, 2),
            2: (2, 2),
        }

        if config.instantMode == -1:        
            top, bottom = config.iModeSplitterSizes
            h = top + bottom
        else:
            top, bottom = instantRatio[config.instantMode]

        self.instantSplitter.setSizes([ h * top // (top + bottom), h * bottom // (top + bottom)])
        
        if config.instantMode:
            self.instantView.show()
        else:
            self.instantView.hide()

    def resizeAsPortrait(self):
               
        parallelRatio = {
            ( 0,  0): (10, 0, 0),
            ( 0,  1): (10, 5, 0),
            ( 0,  2): (5, 5, 0),
            ( 0,  3): (5, 10, 0),
            ( 1,  0): (10, 0, 3),            
            ( 1,  1): (20, 10, 9),
            ( 1,  2): (5, 5, 3),
            ( 1,  3): (10, 20, 9),
            ( 2,  0): (10, 0, 10),
            ( 2,  1): (10, 5, 15),
            ( 2,  2): (10, 10, 20),
            ( 2,  3): (5, 10, 15),
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
