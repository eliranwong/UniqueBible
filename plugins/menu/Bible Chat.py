import config, os, re, openai, sqlite3, webbrowser
from gtts import gTTS
from datetime import datetime
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
    from PySide6.QtWidgets import QWidget, QDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
    from qtpy.QtWidgets import QWidget, QDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox


class ApiDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('API Configuration')

        self.apiKeyEdit = QLineEdit(config.openaiApiKey)
        self.orgEdit = QLineEdit(config.openaiApiOrganization)
        self.contextEdit = QLineEdit(config.chatGPTApiContext)
        self.languageEdit = QLineEdit(config.chatGPTApiAudioLanguage)
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
        layout.addRow(f"{context} [{optional}]:", self.contextEdit)
        layout.addRow(f"{language} [{optional}]:", self.languageEdit)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def api_key(self):
        return self.apiKeyEdit.text().strip()

    def org(self):
        return self.orgEdit.text().strip()

    def context(self):
        return self.contextEdit.text().strip()
    
    def language(self):
        return self.languageEdit.text().strip()


class Database:
    def __init__(self):
        self.connection = sqlite3.connect(os.path.join(config.marvelData, "BibleChat.sqlite"))
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
        # setup interface
        self.setupUI()
        # load database
        self.loadData()
        # new entry at launch
        self.newData()
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)

    def setupVariables(self):
        self.contentID = ""
        self.database = Database()
        self.data_list = []

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
        self.userInput = QLineEdit()
        self.userInput.setPlaceholderText(config.thisTranslation["messageHere"])
        self.userInput.mousePressEvent = lambda _ : self.userInput.selectAll()
        self.userInput.setClearButtonEnabled(True)
        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)
        apiKeyButton = QPushButton(config.thisTranslation["settings"])
        sendButton = QPushButton(config.thisTranslation["send"])
        newButton = QPushButton(config.thisTranslation["new"])
        saveButton = QPushButton(config.thisTranslation["save"])
        self.editableCheckbox = QCheckBox(config.thisTranslation["editable"])
        self.editableCheckbox.setCheckState(Qt.Unchecked)
        self.audioCheckbox = QCheckBox(config.thisTranslation["audio"])
        self.audioCheckbox.setCheckState(Qt.Checked if config.chatGPTApiAudio else Qt.Unchecked)
        self.choiceNumber = QComboBox()
        self.choiceNumber.addItems([str(i) for i in range(1, 11)])
        self.choiceNumber.setCurrentIndex((config.chatGPTApiNoOfChoices - 1))
        self.temperature = QComboBox()
        self.temperature.addItems([str(i/10) for i in range(0, 21)])
        self.temperature.setCurrentIndex(config.chatGPTApiTemperature * 10)
        temperatureLabel = QLabel(config.thisTranslation["temperature"])
        temperatureLabel.setAlignment(Qt.AlignRight)
        choicesLabel = QLabel(config.thisTranslation["choices"])
        choicesLabel.setAlignment(Qt.AlignRight)
        promptLayout = QHBoxLayout()
        promptLayout.addWidget(self.userInput)
        promptLayout.addWidget(sendButton)
        layout000Rt.addLayout(promptLayout)
        layout000Rt.addWidget(self.contentView)
        rtControlLayout = QHBoxLayout()
        rtControlLayout.addWidget(apiKeyButton)
        rtControlLayout.addWidget(temperatureLabel)
        rtControlLayout.addWidget(self.temperature)
        rtControlLayout.addWidget(choicesLabel)
        rtControlLayout.addWidget(self.choiceNumber)
        rtControlLayout.addWidget(self.audioCheckbox)
        rtControlLayout.addWidget(self.editableCheckbox)
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
        self.searchTitle.setPlaceholderText(config.thisTranslation["searchTitleHere"])
        self.searchContent = QLineEdit()
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
        self.userInput.returnPressed.connect(self.displayResponse)
        helpButton.clicked.connect(lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Bible-Chat-with-ChatGPT-API"))
        apiKeyButton.clicked.connect(self.showApiDialog)
        sendButton.clicked.connect(self.displayResponse)
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
        self.choiceNumber.currentIndexChanged.connect(self.updateChoiceNumber)
        self.temperature.currentIndexChanged.connect(self.updateTemperature)

    def showApiDialog(self):
        dialog = ApiDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            config.openaiApiKey = dialog.api_key()
            config.openaiApiOrganization = dialog.org()
            config.chatGPTApiContext = dialog.context()

    def updateTemperature(self, index):
        config.chatGPTApiTemperature = float(index / 10)

    def updateChoiceNumber(self, index):
        config.chatGPTApiNoOfChoices = index + 1

    def toggleEditable(self, state):
        self.contentView.setReadOnly(not state)

    def toggleChatGPTApiAudio(self, state):
        config.chatGPTApiAudio = state
        if not config.chatGPTApiAudio:
            config.mainWindow.closeMediaPlayer()

    def showInProgress(self):
        progress_bar = QProgressBar()
        # Set the progress bar to use an indeterminate progress indicator
        progress_bar.setRange(0, 0)
        layout = QVBoxLayout()
        layout.addWidget(progress_bar)
        widget = QWidget(self)
        widget.setLayout(layout)
        return widget

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
            title = re.sub("^>>> ", "", lines[0][:30])
            content = text
            self.database.insert(self.contentID, title, content)
            self.loadData()

    def loadData(self):
        self.data_list = self.database.search("", "")
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

    def selectData(self, index):
        data = index.data(Qt.UserRole)
        self.contentID = data[0]
        content = data[2]
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

    def displayResponse(self):
        userInput = self.userInput.text().strip()
        if userInput:
            #inProgress = self.showInProgress()
            #inProgress.show()
            responses = self.getResponse(userInput)
            self.contentView.appendPlainText(responses)
            if not (responses.startswith("OpenAI API re") or responses.startswith("Failed to connect to OpenAI API:")):
                self.userInput.setText("")
                if config.chatGPTApiAudio:
                    self.playAudio(responses)
            #inProgress.close()
            # auto-save
            self.saveData()

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

    def getResponse(self, userInput):
        responses = f">>> {userInput}\n\n"
        try:
            self.messages.append({"role": "user", "content": userInput})
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                n=config.chatGPTApiNoOfChoices,
                temperature=config.chatGPTApiTemperature,
            )
            for index, choice in enumerate(completion.choices):
                chat_response = choice.message.content
                if len(completion.choices) > 1:
                    if index > 0:
                        responses += "\n"
                    responses += f"### Response {(index+1)}:\n"
                responses += f"{chat_response}\n\n"
                if index == 0:
                    self.messages.append({"role": "assistant", "content": chat_response})
        # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            return f"OpenAI API returned an API Error: {e}"
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            return f"Failed to connect to OpenAI API: {e}"
        except openai.error.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            return f"OpenAI API request exceeded rate limit: {e}"
        return responses


config.mainWindow.chatGPTapi = ChatGPTAPI(config.mainWindow)
config.mainWindow.chatGPTapi.show()
config.mainWindow.bringToForeground(config.mainWindow.chatGPTapi)
