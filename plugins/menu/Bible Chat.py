import config, os, re, openai, sqlite3, webbrowser, shutil
from gtts import gTTS
if "Pocketsphinx" in config.enabled:
    from pocketsphinx import LiveSpeech, get_model_path
from datetime import datetime
from util.Languages import Languages
from util.FileUtil import FileUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt, QThread, Signal, QRegularExpression
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication, QFontMetrics, QAction, QTextDocument
    from PySide6.QtWidgets import QMainWindow, QWidget, QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox
else:
    from qtpy.QtCore import Qt, QThread, Signal, QRegularExpression
    from qtpy.QtPrintSupport import QPrinter, QPrintDialog
    from qtpy.QtGui import QStandardItemModel, QStandardItem, QGuiApplication, QFontMetrics, QTextDocument
    from qtpy.QtWidgets import QAction, QMainWindow, QWidget, QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox
from gui.Worker import ChatGPTResponse, OpenAIImage


class SpeechRecognitionThread(QThread):
    phrase_recognized = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False

    def run(self):
        self.is_running = True
        if config.pocketsphinxModelPath:
            # download English dictionary at: http://www.speech.cs.cmu.edu/cgi-bin/cmudict
            # download voice models at https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/
            speech = LiveSpeech(
                #sampling_rate=16000,  # optional
                hmm=get_model_path(config.pocketsphinxModelPath),
                lm=get_model_path(config.pocketsphinxModelPathBin),
                dic=get_model_path(config.pocketsphinxModelPathDict),
            )
        else:
            speech = LiveSpeech()

        for phrase in speech:
            if not self.is_running:
                break
            recognized_text = str(phrase)
            self.phrase_recognized.emit(recognized_text)

    def stop(self):
        self.is_running = False


class ApiDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(config.thisTranslation["settings"])

        self.apiKeyEdit = QLineEdit(config.openaiApiKey)
        self.orgEdit = QLineEdit(config.openaiApiOrganization)
        self.maxTokenEdit = QLineEdit(str(config.chatGPTApiMaxTokens))
        self.maxTokenEdit.setToolTip("The maximum number of tokens to generate in the completion.\nThe token count of your prompt plus max_tokens cannot exceed the model's context length. Most models have a context length of 2048 tokens (except for the newest models, which support 4096).")
        self.contextEdit = QLineEdit(config.chatGPTApiContext)
        self.languageBox = QComboBox()
        initialIndex = 0
        index = 0
        for key, value in Languages.gTTSLanguageCodes.items():
            self.languageBox.addItem(key)
            self.languageBox.setItemData(self.languageBox.count()-1, value, role=Qt.ToolTipRole)
            if value == config.chatGPTApiAudioLanguage:
                initialIndex = index
            index += 1
        self.languageBox.setCurrentIndex(initialIndex)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        # https://platform.openai.com/account/api-keys
        context = config.thisTranslation["chatContext"]
        language = config.thisTranslation["menu_language"]
        required = config.thisTranslation["required"]
        optional = config.thisTranslation["optional"]
        layout.addRow(f"OpenAI API Key [{required}]:", self.apiKeyEdit)
        layout.addRow(f"Organization ID [{optional}]:", self.orgEdit)
        layout.addRow(f"Max Token [{required}]:", self.maxTokenEdit)
        layout.addRow(f"{context} [{optional}]:", self.contextEdit)
        layout.addRow(f"{language} [{optional}]:", self.languageBox)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def api_key(self):
        return self.apiKeyEdit.text().strip()

    def org(self):
        return self.orgEdit.text().strip()

    def max_token(self):
        return self.maxTokenEdit.text().strip()

    def context(self):
        return self.contextEdit.text().strip()
    
    def language(self):
        #return self.languageBox.currentText()
        return self.languageBox.currentData(Qt.ToolTipRole)


class Database:
    def __init__(self, filePath=""):
        def regexp(expr, item):
            reg = re.compile(expr, flags=re.IGNORECASE)
            return reg.search(item) is not None
        defaultFilePath = config.chatGPTApiLastChatDatabase if config.chatGPTApiLastChatDatabase and os.path.isfile(config.chatGPTApiLastChatDatabase) else os.path.join(os.path.abspath(config.marvelData), "chats", "default.chat")
        self.filePath = filePath if filePath else defaultFilePath
        self.connection = sqlite3.connect(self.filePath)
        self.connection.create_function("REGEXP", 2, regexp)
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS data (id TEXT PRIMARY KEY, title TEXT, content TEXT)')
        self.connection.commit()

    def insert(self, id, title, content):
        self.cursor.execute('SELECT * FROM data WHERE id = ?', (id,))
        existing_data = self.cursor.fetchone()
        if existing_data:
            if existing_data[1] == title and existing_data[2] == content:
                return
            else:
                self.cursor.execute('UPDATE data SET title = ?, content = ? WHERE id = ?', (title, content, id))
                self.connection.commit()
        else:
            self.cursor.execute('INSERT INTO data (id, title, content) VALUES (?, ?, ?)', (id, title, content))
            self.connection.commit()

    def search(self, title, content):
        if config.chatGPTApiSearchRegexp:
            # with regular expression
            self.cursor.execute('SELECT * FROM data WHERE title REGEXP ? AND content REGEXP ?', (title, content))
        else:
            # without regular expression
            self.cursor.execute('SELECT * FROM data WHERE title LIKE ? AND content LIKE ?', ('%{}%'.format(title), '%{}%'.format(content)))
        return self.cursor.fetchall()

    def delete(self, id):
        self.cursor.execute('DELETE FROM data WHERE id = ?', (id,))
        self.connection.commit()

    def clear(self):
        self.cursor.execute('DELETE FROM data')
        self.connection.commit()


class ChatGPTAPI(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # required
        openai.api_key = os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        # optional
        if config.openaiApiOrganization:
            openai.organization = config.openaiApiOrganization
        # set title
        self.setWindowTitle("Bible Chat")
        #self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # run plugins
        self.runPlugins()
        # setup interface
        self.setupUI()
        # load database
        self.loadData()
        # new entry at launch
        self.newData()
        # set initial window size
        #self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)

    def openDatabase(self):
        # Show a file dialog to get the file path to open
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Database", os.path.join(os.path.abspath(config.marvelData), "chats", "default.chat"), "ChatGPT-GUI Database (*.chat)", options=options)

        # If the user selects a file path, open the file
        self.database = Database(filePath)
        self.loadData()
        self.updateTitle(filePath)

    def newDatabase(self, copyExistingDatabase=False):
        # Show a file dialog to get the file path to save
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getSaveFileName(self, "New Database", os.path.join(os.path.abspath(config.marvelData), "chats", self.database.filePath if copyExistingDatabase else "new.chat"), "ChatGPT-GUI Database (*.chat)", options=options)

        # If the user selects a file path, save the file
        if filePath:
            # make sure the file ends with ".chat"
            if not filePath.endswith(".chat"):
                filePath += ".chat"
            # ignore if copy currently opened database
            if copyExistingDatabase and os.path.abspath(filePath) == os.path.abspath(self.database.filePath):
                return
            # Check if the file already exists
            if os.path.exists(filePath):
                # Ask the user if they want to replace the existing file
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Confirm overwrite")
                msgBox.setText(f"The file {filePath} already exists. Do you want to replace it?")
                msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msgBox.setDefaultButton(QMessageBox.No)
                if msgBox.exec() == QMessageBox.No:
                    return
                else:
                    os.remove(filePath)

            # create a new database
            if copyExistingDatabase:
                shutil.copy(self.database.filePath, filePath)
            self.database = Database(filePath)
            self.loadData()
            self.updateTitle(filePath)

    def updateTitle(self, filePath=""):
        if not filePath:
            filePath = self.database.filePath
        config.chatGPTApiLastChatDatabase = filePath
        basename = os.path.basename(filePath)
        self.parent.setWindowTitle(f"Bible Chat - {basename}")

    def setupVariables(self):
        self.contentID = ""
        self.database = Database()
        self.updateTitle()
        self.data_list = []
        self.recognitionThread = SpeechRecognitionThread(self)
        self.recognitionThread.phrase_recognized.connect(self.onPhraseRecognized)

    def runPlugins(self):
        config.chatGPTTransformers = []
        pluginFolder = os.path.join(os.getcwd(), "plugins", "chatGPT")
        for plugin in FileUtil.fileNamesWithoutExtension(pluginFolder, "py"):
            script = os.path.join(pluginFolder, "{0}.py".format(plugin))
            config.mainWindow.execPythonFile(script)

    def setupUI(self):
        layout000 = QHBoxLayout()
        self.setLayout(layout000)
        widgetLt = QWidget()
        layout000Lt = QVBoxLayout()
        widgetLt.setLayout(layout000Lt)
        widgetRt = QWidget()
        layout000Rt = QVBoxLayout()
        widgetRt.setLayout(layout000Rt)
        
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(widgetLt)
        splitter.addWidget(widgetRt)
        layout000.addWidget(splitter)

        #widgets on the right
        self.searchInput = QLineEdit()
        self.searchInput.setClearButtonEnabled(True)
        self.replaceInput = QLineEdit()
        self.replaceInput.setClearButtonEnabled(True)
        self.userInput = QLineEdit()
        self.userInput.setPlaceholderText(config.thisTranslation["messageHere"])
        self.userInput.mousePressEvent = lambda _ : self.userInput.selectAll()
        self.userInput.setClearButtonEnabled(True)
        self.userInputMultiline = QPlainTextEdit()
        self.userInputMultiline.setPlaceholderText(config.thisTranslation["messageHere"])
        self.voiceCheckbox = QCheckBox(config.thisTranslation["voice"])
        self.voiceCheckbox.setToolTip(config.thisTranslation["voiceTyping"])
        self.voiceCheckbox.setCheckState(Qt.Unchecked)
        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0) # Set the progress bar to use an indeterminate progress indicator
        apiKeyButton = QPushButton(config.thisTranslation["settings"])
        self.multilineButton = QPushButton("+")
        font_metrics = QFontMetrics(self.multilineButton.font())
        text_rect = font_metrics.boundingRect(self.multilineButton.text())
        button_width = text_rect.width() + 20
        button_height = text_rect.height() + 10
        self.multilineButton.setFixedSize(button_width, button_height)
        sendButton = QPushButton(config.thisTranslation["send"])
        searchLabel = QLabel(config.thisTranslation["searchFor"])
        replaceLabel = QLabel(config.thisTranslation["replaceWith"])
        searchReplaceButton = QPushButton(config.thisTranslation["replace"])
        searchReplaceButton.setToolTip(config.thisTranslation["replaceSelectedText"])
        searchReplaceButtonAll = QPushButton(config.thisTranslation["all"])
        searchReplaceButtonAll.setToolTip(config.thisTranslation["replaceAll"])
        self.apiModels = QComboBox()
        self.apiModels.addItems([config.thisTranslation["chat"], config.thisTranslation["image"]])
        self.apiModels.setCurrentIndex(0)
        self.apiModel = 0
        newButton = QPushButton(config.thisTranslation["new"])
        saveButton = QPushButton(config.thisTranslation["save"])
        self.editableCheckbox = QCheckBox(config.thisTranslation["editable"])
        self.editableCheckbox.setCheckState(Qt.Unchecked)
        self.audioCheckbox = QCheckBox(config.thisTranslation["audio"])
        self.audioCheckbox.setCheckState(Qt.Checked if config.chatGPTApiAudio else Qt.Unchecked)
        self.choiceNumber = QComboBox()
        self.choiceNumber.addItems([str(i) for i in range(1, 11)])
        self.choiceNumber.setCurrentIndex((config.chatGPTApiNoOfChoices - 1))
        self.fontSize = QComboBox()
        self.fontSize.addItems([str(i) for i in range(1, 51)])
        self.fontSize.setCurrentIndex((config.chatGPTFontSize - 1))
        self.temperature = QComboBox()
        self.temperature.addItems([str(i/10) for i in range(0, 21)])
        self.temperature.setCurrentIndex(config.chatGPTApiTemperature * 10)
        temperatureLabel = QLabel(config.thisTranslation["temperature"])
        temperatureLabel.setAlignment(Qt.AlignRight)
        temperatureLabel.setToolTip("What sampling temperature to use, between 0 and 2. \nHigher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.")
        choicesLabel = QLabel(config.thisTranslation["choices"])
        choicesLabel.setAlignment(Qt.AlignRight)
        choicesLabel.setToolTip("How many chat completion choices to generate for each input message.")
        fontLabel = QLabel(config.thisTranslation["font"])
        fontLabel.setAlignment(Qt.AlignRight)
        fontLabel.setToolTip(config.thisTranslation["fontSize"])
        promptLayout = QHBoxLayout()
        userInputLayout = QVBoxLayout()
        userInputLayout.addWidget(self.userInput)
        userInputLayout.addWidget(self.userInputMultiline)
        self.userInputMultiline.hide()
        promptLayout.addLayout(userInputLayout)
        if "Pocketsphinx" in config.enabled:
            promptLayout.addWidget(self.voiceCheckbox)
        promptLayout.addWidget(self.multilineButton)
        promptLayout.addWidget(sendButton)
        promptLayout.addWidget(self.apiModels)
        layout000Rt.addLayout(promptLayout)
        layout000Rt.addWidget(self.contentView)
        layout000Rt.addWidget(self.progressBar)
        self.progressBar.hide()
        searchReplaceLayout = QHBoxLayout()
        searchReplaceLayout.addWidget(searchLabel)
        searchReplaceLayout.addWidget(self.searchInput)
        searchReplaceLayout.addWidget(replaceLabel)
        searchReplaceLayout.addWidget(self.replaceInput)
        searchReplaceLayout.addWidget(searchReplaceButton)
        searchReplaceLayout.addWidget(searchReplaceButtonAll)
        layout000Rt.addLayout(searchReplaceLayout)
        rtControlLayout = QHBoxLayout()
        rtControlLayout.addWidget(apiKeyButton)
        rtControlLayout.addWidget(temperatureLabel)
        rtControlLayout.addWidget(self.temperature)
        rtControlLayout.addWidget(choicesLabel)
        rtControlLayout.addWidget(self.choiceNumber)
        rtControlLayout.addWidget(fontLabel)
        rtControlLayout.addWidget(self.fontSize)
        rtControlLayout.addWidget(self.editableCheckbox)
        rtControlLayout.addWidget(self.audioCheckbox)
        rtButtonLayout = QHBoxLayout()
        rtButtonLayout.addWidget(newButton)
        rtButtonLayout.addWidget(saveButton)
        layout000Rt.addLayout(rtControlLayout)
        layout000Rt.addLayout(rtButtonLayout)
        
        #widgets on the left
        helpButton = QPushButton(config.thisTranslation["help"])
        searchTitleButton = QPushButton(config.thisTranslation["searchTitle"])
        searchContentButton = QPushButton(config.thisTranslation["searchContent"])
        self.searchTitle = QLineEdit()
        self.searchTitle.setClearButtonEnabled(True)
        self.searchTitle.setPlaceholderText(config.thisTranslation["searchTitleHere"])
        self.searchContent = QLineEdit()
        self.searchContent.setClearButtonEnabled(True)
        self.searchContent.setPlaceholderText(config.thisTranslation["searchContentHere"])
        self.listView = QListView()
        self.listModel = QStandardItemModel()
        self.listView.setModel(self.listModel)
        removeButton = QPushButton(config.thisTranslation["remove"])
        clearAllButton = QPushButton(config.thisTranslation["clearAll"])
        searchTitleLayout = QHBoxLayout()
        searchTitleLayout.addWidget(self.searchTitle)
        searchTitleLayout.addWidget(searchTitleButton)
        layout000Lt.addLayout(searchTitleLayout)
        searchContentLayout = QHBoxLayout()
        searchContentLayout.addWidget(self.searchContent)
        searchContentLayout.addWidget(searchContentButton)
        layout000Lt.addLayout(searchContentLayout)
        layout000Lt.addWidget(self.listView)
        ltButtonLayout = QHBoxLayout()
        ltButtonLayout.addWidget(removeButton)
        ltButtonLayout.addWidget(clearAllButton)
        layout000Lt.addLayout(ltButtonLayout)
        layout000Lt.addWidget(helpButton)
        
        # Connections
        self.userInput.returnPressed.connect(self.sendMessage)
        helpButton.clicked.connect(lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Bible-Chat-with-ChatGPT-API"))
        apiKeyButton.clicked.connect(self.showApiDialog)
        self.multilineButton.clicked.connect(self.multilineButtonClicked)
        sendButton.clicked.connect(self.sendMessage)
        saveButton.clicked.connect(self.saveData)
        newButton.clicked.connect(self.newData)
        searchTitleButton.clicked.connect(self.searchData)
        searchContentButton.clicked.connect(self.searchData)
        self.searchTitle.textChanged.connect(self.searchData)
        self.searchContent.textChanged.connect(self.searchData)
        self.listView.clicked.connect(self.selectData)
        clearAllButton.clicked.connect(self.clearData)
        removeButton.clicked.connect(self.removeData)
        self.editableCheckbox.stateChanged.connect(self.toggleEditable)
        self.audioCheckbox.stateChanged.connect(self.toggleChatGPTApiAudio)
        self.voiceCheckbox.stateChanged.connect(self.toggleVoiceTyping)
        self.choiceNumber.currentIndexChanged.connect(self.updateChoiceNumber)
        self.apiModels.currentIndexChanged.connect(self.updateApiModel)
        self.fontSize.currentIndexChanged.connect(self.setFontSize)
        self.temperature.currentIndexChanged.connect(self.updateTemperature)
        searchReplaceButton.clicked.connect(self.replaceSelectedText)
        searchReplaceButtonAll.clicked.connect(self.searchReplaceAll)
        self.searchInput.returnPressed.connect(self.searchChatContent)
        self.replaceInput.returnPressed.connect(self.replaceSelectedText)

        self.updateSearchToolTips()

    def setFontSize(self, index=None):
        if index is not None:
            config.chatGPTFontSize = index + 1
        # content view
        font = self.contentView.font()
        font.setPointSize(config.chatGPTFontSize)
        self.contentView.setFont(font)
        # list view
        font = self.listView.font()
        font.setPointSize(config.chatGPTFontSize)
        self.listView.setFont(font)

    def updateSearchToolTips(self):
        if config.chatGPTApiSearchRegexp:
            self.searchTitle.setToolTip(config.thisTranslation["matchingRegularExpression"])
            self.searchContent.setToolTip(config.thisTranslation["matchingRegularExpression"])
            self.searchInput.setToolTip(config.thisTranslation["matchingRegularExpression"])
        else:
            self.searchTitle.setToolTip("")
            self.searchContent.setToolTip("")
            self.searchInput.setToolTip("")

    def searchChatContent(self):
        searchInput = self.searchInput.text()
        search = QRegularExpression(searchInput) if config.chatGPTApiSearchRegexp else searchInput
        self.contentView.find(search)

    def replaceSelectedText(self):
        currentSelectedText = self.contentView.textCursor().selectedText()
        if not currentSelectedText == "":
            searchInput = self.searchInput.text()
            replaceInput = self.replaceInput.text()
            if searchInput:
                replace = re.sub(searchInput, replaceInput, currentSelectedText) if config.chatGPTApiSearchRegexp else currentSelectedText.replace(searchInput, replaceInput)
            else:
                replace = self.replaceInput.text()
            self.contentView.insertPlainText(replace)

    def searchReplaceAll(self):
        search = self.searchInput.text()
        if search:
            replace = self.replaceInput.text()
            content = self.contentView.toPlainText()
            newContent = re.sub(search, replace, content, flags=re.M) if config.chatGPTApiSearchRegexp else content.replace(search, replace)
            self.contentView.setPlainText(newContent)

    def multilineButtonClicked(self):
        if self.userInput.isVisible():
            self.userInput.hide()
            self.userInputMultiline.setPlainText(self.userInput.text())
            self.userInputMultiline.show()
            self.multilineButton.setText("-")
        else:
            self.userInputMultiline.hide()
            self.userInput.setText(self.userInputMultiline.toPlainText())
            self.userInput.show()
            self.multilineButton.setText("+")

    def showApiDialog(self):
        dialog = ApiDialog(self)
        result = dialog.exec() if config.qtLibrary == "pyside6" else dialog.exec_()
        if result == QDialog.Accepted:
            config.openaiApiKey = dialog.api_key()
            if not openai.api_key:
                openai.api_key = os.environ["OPENAI_API_KEY"] = config.openaiApiKey
            config.openaiApiOrganization = dialog.org()
            try:
                config.chatGPTApiMaxTokens = int(dialog.max_token())
            except:
                pass
            config.chatGPTApiContext = dialog.context()
            config.chatGPTApiAudioLanguage = dialog.language()
            self.newData()

    def updateApiModel(self, index):
        self.apiModel = index

    def updateTemperature(self, index):
        config.chatGPTApiTemperature = float(index / 10)

    def updateChoiceNumber(self, index):
        config.chatGPTApiNoOfChoices = index + 1

    def onPhraseRecognized(self, phrase):
        self.userInput.setText(f"{self.userInput.text()} {phrase}")

    def toggleVoiceTyping(self, state):
        self.recognitionThread.start() if state else self.recognitionThread.stop()

    def toggleEditable(self, state):
        self.contentView.setReadOnly(not state)

    def toggleChatGPTApiAudio(self, state):
        config.chatGPTApiAudio = state
        if not config.chatGPTApiAudio:
            config.mainWindow.closeMediaPlayer()

    def removeData(self):
        index = self.listView.selectedIndexes()
        if not index:
            return
        confirm = QMessageBox.question(self, config.thisTranslation["remove"], config.thisTranslation["areyousure"], QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            item = index[0]
            data = item.data(Qt.UserRole)
            self.database.delete(data[0])
            self.loadData()

    def clearData(self):
        confirm = QMessageBox.question(self, config.thisTranslation["clearAll"], config.thisTranslation["areyousure"], QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.database.clear()
            self.loadData()

    def saveData(self):
        text = self.contentView.toPlainText().strip()
        if text:
            lines = text.split("\n")
            if not self.contentID:
                self.contentID = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            title = re.sub("^>>> ", "", lines[0][:50])
            content = text
            self.database.insert(self.contentID, title, content)
            self.loadData()

    def loadData(self):
        # reverse the list, so that the latest is on the top
        self.data_list = self.database.search("", "")
        if self.data_list:
            self.data_list.reverse()
        self.listModel.clear()
        for data in self.data_list:
            item = QStandardItem(data[1])
            item.setToolTip(data[0])
            item.setData(data, Qt.UserRole)
            self.listModel.appendRow(item)

    def searchData(self):
        keyword1 = self.searchTitle.text().strip()
        keyword2 = self.searchContent.text().strip()
        self.data_list = self.database.search(keyword1, keyword2)
        self.listModel.clear()
        for data in self.data_list:
            item = QStandardItem(data[1])
            item.setData(data, Qt.UserRole)
            self.listModel.appendRow(item)

    def newData(self):
        self.contentID = ""
        self.contentView.setPlainText("" if openai.api_key else """OpenAI API Key is NOT Found!

Follow the following steps:
1) Register and get your OpenAI Key at https://platform.openai.com/account/api-keys
2) Click the "Settings" button below and enter your own OpenAI API key""")
        self.resetMessages()
        self.userInput.setFocus()

    def selectData(self, index):
        data = index.data(Qt.UserRole)
        self.contentID = data[0]
        content = data[2]
        self.resetContent(content)
        self.userInput.setFocus()

    def printData(self):
        # Get the printer and print dialog
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        # If the user clicked "OK" in the print dialog, print the text
        if dialog.exec() == QPrintDialog.Accepted:
            document = QTextDocument()
            document.setPlainText(self.contentView.toPlainText())
            document.print_(printer)

    def resetContent(self, content):
        self.contentView.setPlainText(content)
        # update context
        self.resetMessages()
        self.messages.append({"role": "assistant", "content": content})

    def resetMessages(self):
        self.messages = [
            {"role": "system", "content" : "You’re a kind helpful assistant"}
        ]
        if config.chatGPTApiContext:
            self.messages.append({"role": "assistant", "content" : config.chatGPTApiContext})

    def print(self, text):
        self.contentView.appendPlainText(f"\n{text}" if self.contentView.toPlainText() else text)
        self.contentView.setPlainText(re.sub("\n\n[\n]+?([^\n])", r"\n\n\1", self.contentView.toPlainText()))

    def sendMessage(self):
        if self.userInputMultiline.isVisible():
            self.multilineButtonClicked()
        if self.apiModel == 0:
            self.getResponse()
        else:
            self.getImage()

    def getImage(self):
        userInput = self.userInput.text().strip()
        if userInput:
            self.userInput.setDisabled(True)
            self.progressBar.show() # show progress bar
            OpenAIImage(self).workOnGetResponse(userInput)

    def displayImage(self, imageUrl):
        webbrowser.open(imageUrl)
        self.userInput.setEnabled(True)
        self.progressBar.hide()

    def getResponse(self):
        userInput = self.userInput.text().strip()
        if userInput:
            self.userInput.setDisabled(True)
            self.print(f">>> {userInput}")
            self.saveData()
            self.currentLoadingID = self.contentID
            self.currentLoadingContent = self.contentView.toPlainText().strip()
            self.progressBar.show() # show progress bar
            self.messages.append({"role": "user", "content": userInput}) # update messages
            ChatGPTResponse(self).workOnGetResponse(self.messages) # get chatGPT response in a separate thread

    def processResponse(self, responses):
        # reload the working content in case users change it during waiting for response
        self.contentID = self.currentLoadingID
        self.resetContent(self.currentLoadingContent)
        self.currentLoadingID = self.currentLoadingContent = ""
        # transform responses
        for t in config.chatGPTTransformers:
            responses = t(responses)
        # update new reponses
        self.print(responses)
        # scroll to the bottom
        contentScrollBar = self.contentView.verticalScrollBar()
        contentScrollBar.setValue(contentScrollBar.maximum())
        if not (responses.startswith("OpenAI API re") or responses.startswith("Failed to connect to OpenAI API:")):
            self.userInput.setText("")
            if config.chatGPTApiAudio:
                self.playAudio(responses)
        # auto-save
        self.saveData()
        # hide progress bar
        self.userInput.setEnabled(True)
        self.progressBar.hide()
        self.userInput.setFocus()

    def playAudio(self, responses):
        textList = [i.replace(">>>", "").strip() for i in responses.split("\n") if i.strip()]
        audioFiles = []
        for index, text in enumerate(textList):
            try:
                audioFile = os.path.abspath(os.path.join("temp", f"gtts_{index}.mp3"))
                if os.path.isfile(audioFile):
                    os.remove(audioFile)
                gTTS(text=text, lang=config.chatGPTApiAudioLanguage if config.chatGPTApiAudioLanguage else "en").save(audioFile)
                audioFiles.append(audioFile)
            except:
                pass
        if audioFiles:
            config.mainWindow.playAudioBibleFilePlayList(audioFiles)


class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Set a central widget
        self.chatGPT = ChatGPTAPI(self)
        self.setCentralWidget(self.chatGPT)

        # Create a menu bar
        menubar = self.menuBar()

        # Create a File menu and add it to the menu bar
        file_menu = menubar.addMenu(config.thisTranslation["chat"])

        new_action = QAction(config.thisTranslation["openDatabase"], self)
        new_action.setShortcut("Ctrl+Shift+O")
        new_action.triggered.connect(self.chatGPT.openDatabase)
        file_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["newDatabase"], self)
        new_action.setShortcut("Ctrl+Shift+N")
        new_action.triggered.connect(self.chatGPT.newDatabase)
        file_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["saveDatabaseAs"], self)
        new_action.setShortcut("Ctrl+Shift+S")
        new_action.triggered.connect(lambda: self.chatGPT.newDatabase(copyExistingDatabase=True))
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction(config.thisTranslation["newChat"], self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.chatGPT.newData)
        file_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["saveChat"], self)
        new_action.setShortcut("Ctrl+S")
        new_action.triggered.connect(self.chatGPT.saveData)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction(config.thisTranslation["printChat"], self)
        new_action.setShortcut("Ctrl+P")
        new_action.triggered.connect(self.chatGPT.printData)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        openSettings = QAction(config.thisTranslation["chatSettings"], self)
        openSettings.triggered.connect(self.chatGPT.showApiDialog)
        file_menu.addAction(openSettings)

        new_action = QAction(config.thisTranslation["toggleRegexp"], self)
        new_action.triggered.connect(self.toggleRegexp)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Create a Exit action and add it to the File menu
        exit_action = QAction(config.thisTranslation["exit"], self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # set initial window size
        #self.setWindowTitle("Bible Chat")
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
        self.show()
        self.chatGPT.setFontSize()

    def toggleRegexp(self):
        config.chatGPTApiSearchRegexp = not config.chatGPTApiSearchRegexp
        self.chatGPT.updateSearchToolTips()
        QMessageBox.information(self, "ChatGPT-GUI", f"Regular expression for search and replace is {'enabled' if config.chatGPTApiSearchRegexp else 'disabled'}!")

#config.mainWindow.chatGPTapi = ChatGPTAPI(config.mainWindow)
#config.mainWindow.chatGPTapi.show()
#config.mainWindow.bringToForeground(config.mainWindow.chatGPTapi)
#config.mainWindow.chatGPTapi.setFontSize()

bibleChat = MainWindow(config.mainWindow)
bibleChat.show()

# load selected text, if any, to user input
selectedText = config.mainWindow.selectedText()
if selectedText:
    bibleChat.chatGPT.userInput.setText(selectedText)