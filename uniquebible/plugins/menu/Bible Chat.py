from uniquebible import config, isLLMReady
import os, re, openai, tiktoken, sqlite3, webbrowser, shutil, platform
import subprocess, traceback, sys
import urllib.parse
from io import StringIO
from functools import partial
from gtts import gTTS
if "Pocketsphinx" in config.enabled:
    from pocketsphinx import LiveSpeech, get_model_path
from datetime import datetime
from uniquebible.util.Languages import Languages
from uniquebible.util.FileUtil import FileUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt, QThread, Signal, QRegularExpression
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication, QFontMetrics, QAction, QTextDocument
    from PySide6.QtWidgets import QCompleter, QMainWindow, QWidget, QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox
else:
    from qtpy.QtCore import Qt, QThread, Signal, QRegularExpression
    from qtpy.QtPrintSupport import QPrinter, QPrintDialog
    from qtpy.QtGui import QStandardItemModel, QStandardItem, QGuiApplication, QFontMetrics, QTextDocument
    from qtpy.QtWidgets import QCompleter, QAction, QMainWindow, QWidget, QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox
from uniquebible.gui.Worker import ChatGPTResponse, OpenAIImage


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
        if config.llm_backend == "openai":
            self.apiKeyEdit = QLineEdit(config.openaiApi_key)
        elif config.llm_backend == "azure":
            self.apiKeyEdit = QLineEdit(config.azureApi_key)
        elif config.llm_backend == "google":
            self.apiKeyEdit = QLineEdit(config.googleaiApi_key)
        elif config.llm_backend == "mistral":
            self.apiKeyEdit = QLineEdit(str(config.mistralApi_key))
        elif config.llm_backend == "grok":
            self.apiKeyEdit = QLineEdit(str(config.grokApi_key))
        elif config.llm_backend == "groq":
            self.apiKeyEdit = QLineEdit(str(config.groqApi_key))
        elif config.llm_backend == "github":
            self.apiKeyEdit = QLineEdit(str(config.githubApi_key))
        self.apiKeyEdit.setEchoMode(QLineEdit.Password)
        #self.orgEdit = QLineEdit(config.openaiApiOrganization)
        #self.orgEdit.setEchoMode(QLineEdit.Password)
        self.apiModelBox = QComboBox()
        initialIndex = 0
        index = 0
        if config.llm_backend in ("openai", "github"):
            for key in ("gpt-4o", "gpt-4o-mini"):
                self.apiModelBox.addItem(key)
                if key == config.openaiApi_chat_model:
                    initialIndex = index
                index += 1
        elif config.llm_backend == "azure":
            for key in config.azureOpenAIModels: # users can manually change config.azureOpenAIModels to match custom deployed model names
                self.apiModelBox.addItem(key)
                if key == config.openaiApi_chat_model:
                    initialIndex = index
                index += 1
        elif config.llm_backend == "google":
            for key in ("gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"):
                self.apiModelBox.addItem(key)
                if key == config.googleaiApi_chat_model:
                    initialIndex = index
                index += 1
        elif config.llm_backend == "mistral":
            for key in ("mistral-large-latest", "ministral-8b-latest", "ministral-3b-latest"):
                self.apiModelBox.addItem(key)
                if key == config.mistralApi_chat_model:
                    initialIndex = index
                index += 1
        elif config.llm_backend == "grok":
            for key in ("grok-beta",):
                self.apiModelBox.addItem(key)
                if key == config.grokApi_chat_model:
                    initialIndex = index
                index += 1
        elif config.llm_backend == "groq":
            for key in ("gemma2-9b-it", "gemma-7b-it", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-1b-preview", "llama-3.2-3b-preview", "llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"):
                self.apiModelBox.addItem(key)
                if key == config.groqApi_chat_model:
                    initialIndex = index
                index += 1
        self.apiModelBox.setCurrentIndex(initialIndex)
        self.functionCallingBox = QComboBox()
        initialIndex = 0
        index = 0
        for key in ("auto", "none"):
            self.functionCallingBox.addItem(key)
            if key == config.chatApiFunctionCall:
                initialIndex = index
            index += 1
        self.functionCallingBox.setCurrentIndex(initialIndex)
        self.loadingInternetSearchesBox = QComboBox()
        initialIndex = 0
        index = 0
        for key in ("always", "auto", "none"):
            self.loadingInternetSearchesBox.addItem(key)
            if key == config.chatApiLoadingInternetSearches:
                initialIndex = index
            index += 1
        self.loadingInternetSearchesBox.setCurrentIndex(initialIndex)
        if config.llm_backend in ("openai", "github", "azure"):
            self.maxTokenEdit = QLineEdit(str(config.openaiApi_chat_model_max_tokens))
        elif config.llm_backend == "google":
            self.maxTokenEdit = QLineEdit(str(config.googleaiApi_chat_model_max_tokens))
        elif config.llm_backend == "mistral":
            self.maxTokenEdit = QLineEdit(str(config.mistralApi_chat_model_max_tokens))
        elif config.llm_backend == "grok":
            self.maxTokenEdit = QLineEdit(str(config.grokApi_chat_model_max_tokens))
        elif config.llm_backend == "groq":
            self.maxTokenEdit = QLineEdit(str(config.groqApi_chat_model_max_tokens))
        self.maxTokenEdit.setToolTip("The maximum number of tokens to generate in the completion.\nThe token count of your prompt plus max_tokens cannot exceed the model's context length. Most models have a context length of 2048 tokens (except for the newest models, which support 4096).")
        self.maxInternetSearchResults = QLineEdit(str(config.chatGPTApiMaximumInternetSearchResults))
        self.maxInternetSearchResults.setToolTip("The maximum number of internet search response to be included.")
        #self.includeInternetSearches = QCheckBox(config.thisTranslation["include"])
        #self.includeInternetSearches.setToolTip("Include latest internet search results")
        #self.includeInternetSearches.setCheckState(Qt.Checked if config.chatGPTApiIncludeDuckDuckGoSearchResults else Qt.Unchecked)
        #self.includeDuckDuckGoSearchResults = config.chatGPTApiIncludeDuckDuckGoSearchResults
        self.autoScrollingCheckBox = QCheckBox(config.thisTranslation["enable"])
        self.autoScrollingCheckBox.setToolTip("Auto-scroll display as responses are received")
        self.autoScrollingCheckBox.setCheckState(Qt.Checked if config.chatGPTApiAutoScrolling else Qt.Unchecked)
        self.chatGPTApiAutoScrolling = config.chatGPTApiAutoScrolling
        self.chatAfterFunctionCalledCheckBox = QCheckBox(config.thisTranslation["enable"])
        self.chatAfterFunctionCalledCheckBox.setToolTip("Automatically generate next chat response after a function is called")
        self.chatAfterFunctionCalledCheckBox.setCheckState(Qt.Checked if config.chatAfterFunctionCalled else Qt.Unchecked)
        self.chatAfterFunctionCalled = config.chatAfterFunctionCalled
        self.runPythonScriptGloballyCheckBox = QCheckBox(config.thisTranslation["enable"])
        self.runPythonScriptGloballyCheckBox.setToolTip("Run user python script in global scope")
        self.runPythonScriptGloballyCheckBox.setCheckState(Qt.Checked if config.runPythonScriptGlobally else Qt.Unchecked)
        self.runPythonScriptGlobally = config.runPythonScriptGlobally
        self.contextEdit = QLineEdit(config.chatGPTApiContext)
        #firstInputOnly = config.thisTranslation["firstInputOnly"]
        #allInputs = config.thisTranslation["allInputs"]
        #self.applyContextIn = QComboBox()
        #self.applyContextIn.addItems([firstInputOnly, allInputs])
        #self.applyContextIn.setCurrentIndex(1 if config.chatGPTApiContextInAllInputs else 0)
        self.contextEdit.setEnabled(True)
        #self.contextEdit.setDisabled(True) if not initialIndex == 1 else self.contextEdit.setEnabled(True)
        """self.languageBox = QComboBox()
        initialIndex = 0
        index = 0
        for key, value in Languages.gTTSLanguageCodes.items():
            self.languageBox.addItem(key)
            self.languageBox.setItemData(self.languageBox.count()-1, value, role=Qt.ToolTipRole)
            if value == config.chatGPTApiAudioLanguage:
                initialIndex = index
            index += 1
        self.languageBox.setCurrentIndex(initialIndex)"""
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout()
        # https://platform.openai.com/account/api-keys
        #chatAfterFunctionCalled = config.thisTranslation["chatAfterFunctionCalled"]
        #runPythonScriptGlobally = config.thisTranslation["runPythonScriptGlobally"]
        autoScroll = config.thisTranslation["autoScroll"]
        context = config.thisTranslation["chatContext"]
        #applyContext = config.thisTranslation["applyContext"]
        #latestOnlineSearchResults = config.thisTranslation["latestOnlineSearchResults"]
        #maximumOnlineSearchResults = config.thisTranslation["maximumOnlineSearchResults"]
        #language = config.thisTranslation["menu_language"]
        required = config.thisTranslation["required"]
        optional = config.thisTranslation["optional"]
        custom = config.thisTranslation["custom"].lower()
        layout.addRow(f"{config.llm_backend.capitalize()} API Key [{required}]:", self.apiKeyEdit)
        if config.llm_backend == "azure":
            self.azureBaseUrl = QLineEdit(config.azureBaseUrl)
            layout.addRow(f"Azure endpoint [{required}]:", self.azureBaseUrl)
        #layout.addRow(f"Organization ID [{optional}]:", self.orgEdit)
        layout.addRow(f"Chat Model [{required}]:", self.apiModelBox)
        layout.addRow(f"Max Token [{required}]:", self.maxTokenEdit)
        #layout.addRow(f"Function Calling [{optional}]:", self.functionCallingBox)
        #layout.addRow(f"{chatAfterFunctionCalled} [{optional}]:", self.chatAfterFunctionCalledCheckBox)
        layout.addRow(f"{context} [{custom}]:", self.contextEdit)
        #layout.addRow(f"{applyContext} [{optional}]:", self.applyContextIn)
        #layout.addRow(f"{latestOnlineSearchResults} [{optional}]:", self.loadingInternetSearchesBox)
        #layout.addRow(f"{maximumOnlineSearchResults} [{optional}]:", self.maxInternetSearchResults)
        layout.addRow(f"{autoScroll} [{optional}]:", self.autoScrollingCheckBox)
        #layout.addRow(f"{runPythonScriptGlobally} [{optional}]:", self.runPythonScriptGloballyCheckBox)
        #layout.addRow(f"{language} [{optional}]:", self.languageBox)
        layout.addWidget(buttonBox)
        self.autoScrollingCheckBox.stateChanged.connect(self.toggleAutoScrollingCheckBox)
        #self.chatAfterFunctionCalledCheckBox.stateChanged.connect(self.toggleChatAfterFunctionCalled)
        #self.runPythonScriptGloballyCheckBox.stateChanged.connect(self.toggleRunPythonScriptGlobally)
        #self.functionCallingBox.currentIndexChanged.connect(self.functionCallingBoxChanged)
        #self.loadingInternetSearchesBox.currentIndexChanged.connect(self.loadingInternetSearchesBoxChanged)

        self.setLayout(layout)

    def api_key(self):
        return self.apiKeyEdit.text().strip()

    def org(self):
        return self.orgEdit.text().strip()

    def contextInAllInputs(self):
        return True if self.applyContextIn.currentIndex() == 1 else False

    def apiModel(self):
        #return "gpt-3.5-turbo"
        return self.apiModelBox.currentText()

    def functionCalling(self):
        return self.functionCallingBox.currentText()

    def functionCallingBoxChanged(self):
        if self.functionCallingBox.currentText() == "none" and self.loadingInternetSearchesBox.currentText() == "auto":
            self.loadingInternetSearchesBox.setCurrentText("none")

    def loadingInternetSearches(self):
        return self.loadingInternetSearchesBox.currentText()

    def loadingInternetSearchesBoxChanged(self, _):
        if self.loadingInternetSearchesBox.currentText() == "auto":
            self.functionCallingBox.setCurrentText("auto")

    def max_token(self):
        return self.maxTokenEdit.text().strip()

    def enable_auto_scrolling(self):
        return self.chatGPTApiAutoScrolling

    def toggleAutoScrollingCheckBox(self, state):
        self.chatGPTApiAutoScrolling = True if state else False

    def enable_chatAfterFunctionCalled(self):
        return self.chatAfterFunctionCalled

    def toggleChatAfterFunctionCalled(self, state):
        self.chatAfterFunctionCalled = True if state else False

    def enable_runPythonScriptGlobally(self):
        return self.runPythonScriptGlobally

    def toggleRunPythonScriptGlobally(self, state):
        self.runPythonScriptGlobally = True if state else False

    def max_internet_search_results(self):
        return self.maxInternetSearchResults.text().strip()

    def context(self):
        return self.contextEdit.text().strip()
    
    """def language(self):
        #return self.languageBox.currentText()
        return self.languageBox.currentData(Qt.ToolTipRole)"""


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
        config.chatGPTApi = self
        self.parent = parent
        # required
        os.environ["OPENAI_API_KEY"] = config.openaiApi_key
        # set title
        self.setWindowTitle("Bible Chat")
        #self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # run plugins
        #self.runPlugins()
        config.mainWindow.runBibleChatPlugins()
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
        self.newData()

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
            self.newData()

    def updateTitle(self, filePath=""):
        if not filePath:
            filePath = self.database.filePath
        config.chatGPTApiLastChatDatabase = filePath
        basename = os.path.basename(filePath)
        self.parent.setWindowTitle(f"Bible Chat - {basename}")

    def setupVariables(self):
        self.busyLoading = False
        self.contentID = ""
        self.database = Database()
        self.updateTitle()
        self.data_list = []
        self.recognitionThread = SpeechRecognitionThread(self)
        self.recognitionThread.phrase_recognized.connect(self.onPhraseRecognized)
        self.recentCommands = []

    """def runPlugins(self):
        # The following config values can be modified with plugins, to extend functionalities
        config.predefinedContexts = {
            "[none]": "",
            "[custom]": "",
        }
        config.inputSuggestions = []
        config.chatGPTTransformers = []
        config.chatGPTApiFunctionSignatures = []
        config.chatGPTApiAvailableFunctions = {}

        pluginFolder = os.path.join(config.packageDir, "plugins", "chatGPT")
        for plugin in FileUtil.fileNamesWithoutExtension(pluginFolder, "py"):
            script = os.path.join(pluginFolder, "{0}.py".format(plugin))
            config.mainWindow.execPythonFile(script)"""

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
        completer = QCompleter(config.inputSuggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.userInput.setCompleter(completer)
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
        self.sendButton = QPushButton(config.thisTranslation["send"])
        searchLabel = QLabel(config.thisTranslation["searchFor"])
        replaceLabel = QLabel(config.thisTranslation["replaceWith"])
        searchReplaceButton = QPushButton(config.thisTranslation["replace"])
        searchReplaceButton.setToolTip(config.thisTranslation["replaceSelectedText"])
        searchReplaceButtonAll = QPushButton(config.thisTranslation["all"])
        searchReplaceButtonAll.setToolTip(config.thisTranslation["replaceAll"])
        self.apiModels = QComboBox()
        self.apiModels.addItems([config.thisTranslation["chat"], config.thisTranslation["image"], "browser", "python", "system"])
        self.apiModels.setCurrentIndex(0)
        self.apiModel = 0
        self.newButton = QPushButton(config.thisTranslation["new"])
        saveButton = QPushButton(config.thisTranslation["save"])
        self.editableCheckbox = QCheckBox(config.thisTranslation["editable"])
        self.editableCheckbox.setCheckState(Qt.Unchecked)
        self.audioCheckbox = QCheckBox(config.thisTranslation["audio"])
        self.audioCheckbox.setCheckState(Qt.Checked if config.chatGPTApiAudio else Qt.Unchecked)
        #self.choiceNumber = QComboBox()
        #self.choiceNumber.addItems([str(i) for i in range(1, 11)])
        #self.choiceNumber.setCurrentIndex((config.chatApiNoOfChoices - 1))
        self.backends = QComboBox()
        self.backends.addItems(config.llm_backends)
        if config.llm_backend == "openai":
            self.backends.setCurrentIndex(0)
        elif config.llm_backend == "github":
            self.backends.setCurrentIndex(1)
        elif config.llm_backend == "azure":
            self.backends.setCurrentIndex(2)
        elif config.llm_backend == "google":
            self.backends.setCurrentIndex(3)
        elif config.llm_backend == "groq":
            self.backends.setCurrentIndex(4)
        elif config.llm_backend == "mistral":
            self.backends.setCurrentIndex(5)
        elif config.llm_backend == "grok":
            self.backends.setCurrentIndex(6)
        else:
            config.llm_backend == "groq"
            self.backends.setCurrentIndex(4)
        self.fontSize = QComboBox()
        self.fontSize.addItems([str(i) for i in range(1, 51)])
        self.fontSize.setCurrentIndex((config.chatGPTFontSize - 1))
        self.temperature = QComboBox()
        self.temperature.addItems([str(i/10) for i in range(0, 21)])
        if config.llm_backend in ("openai", "github", "azure"):
            self.temperature.setCurrentIndex(int(config.openaiApi_llmTemperature * 10))
        elif config.llm_backend == "google":
            self.temperature.setCurrentIndex(int(config.googleaiApi_llmTemperature * 10))
        elif config.llm_backend == "grok":
            self.temperature.setCurrentIndex(int(config.grokApi_llmTemperature * 10))
        elif config.llm_backend == "groq":
            self.temperature.setCurrentIndex(int(config.groqApi_llmTemperature * 10))
        elif config.llm_backend == "mistral":
            self.temperature.setCurrentIndex(int(config.mistralApi_llmTemperature * 10))
        temperatureLabel = QLabel(config.thisTranslation["temperature"])
        temperatureLabel.setAlignment(Qt.AlignRight)
        temperatureLabel.setToolTip("What sampling temperature to use, between 0 and 2. \nHigher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.")
        #choicesLabel = QLabel(config.thisTranslation["choices"])
        #choicesLabel.setAlignment(Qt.AlignRight)
        #choicesLabel.setToolTip("How many chat completion choices to generate for each input message.")
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
        promptLayout.addWidget(self.sendButton)
        #promptLayout.addWidget(self.apiModels)
        layout000Rt.addLayout(promptLayout)

        self.predefinedContextBox = QComboBox()
        initialIndex = 0
        index = 0
        for key, value in config.predefinedContexts.items():
            self.predefinedContextBox.addItem(key)
            self.predefinedContextBox.setItemData(self.predefinedContextBox.count()-1, value, role=Qt.ToolTipRole)
            if key == config.chatGPTApiPredefinedContext:
                initialIndex = index
            index += 1
        self.predefinedContextBox.currentIndexChanged.connect(self.predefinedContextBoxChanged)
        self.predefinedContextBox.setCurrentIndex(initialIndex)

        predefinedSelectionLayout = QHBoxLayout()
        predefinedSelectionLayout.addWidget(self.predefinedContextBox)
        layout000Rt.addLayout(predefinedSelectionLayout)

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
        rtControlLayout.addWidget(self.backends)
        rtControlLayout.addWidget(apiKeyButton)
        rtControlLayout.addWidget(temperatureLabel)
        rtControlLayout.addWidget(self.temperature)
        #rtControlLayout.addWidget(choicesLabel)
        #rtControlLayout.addWidget(self.choiceNumber)
        rtControlLayout.addWidget(fontLabel)
        rtControlLayout.addWidget(self.fontSize)
        rtControlLayout.addWidget(self.editableCheckbox)
        rtControlLayout.addWidget(self.audioCheckbox)
        if config.chatApiNoOfChoices == 1:
            self.audioCheckbox.hide()
        rtButtonLayout = QHBoxLayout()
        rtButtonLayout.addWidget(self.newButton)
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
        self.sendButton.clicked.connect(self.sendMessage)
        saveButton.clicked.connect(self.saveData)
        self.newButton.clicked.connect(self.newData)
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
        #self.choiceNumber.currentIndexChanged.connect(self.updateChoiceNumber)
        self.apiModels.currentIndexChanged.connect(self.updateApiModel)
        self.fontSize.currentIndexChanged.connect(self.setFontSize)
        self.temperature.currentIndexChanged.connect(self.updateTemperature)
        self.backends.currentIndexChanged.connect(self.updateBackend)
        searchReplaceButton.clicked.connect(self.replaceSelectedText)
        searchReplaceButtonAll.clicked.connect(self.searchReplaceAll)
        self.searchInput.returnPressed.connect(self.searchChatContent)
        self.replaceInput.returnPressed.connect(self.replaceSelectedText)

        self.updateSearchToolTips()

    def predefinedContextBoxChanged(self, index):
        self.setUserInputFocus()
        config.chatGPTApiPredefinedContext = self.predefinedContextBox.currentText()
        desc = config.predefinedContexts[self.predefinedContextBox.currentText()]
        self.predefinedContextBox.setToolTip(desc)

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
        self.setUserInputFocus()

    def setUserInputFocus(self):
        self.userInput.setFocus() if self.userInput.isVisible() else self.userInputMultiline.setFocus()

    def showApiDialog(self):
        dialog = ApiDialog(self)
        result = dialog.exec() if config.qtLibrary == "pyside6" else dialog.exec_()
        if result == QDialog.Accepted:
            if config.llm_backend == "openai":
                config.openaiApi_key = dialog.api_key()
            elif config.llm_backend == "azure":
                config.azureApi_key = dialog.api_key()
                config.azureBaseUrl = dialog.azureBaseUrl.text().strip()
            elif config.llm_backend == "google":
                config.googleaiApi_key = dialog.api_key()
            elif config.llm_backend == "grok":
                config.grokApi_key = dialog.api_key()
            elif config.llm_backend == "mistral":
                config.mistralApi_key = dialog.api_key()
                try:
                    check = eval(config.mistralApi_key)
                    if isinstance(check, list):
                        config.mistralApi_key = check
                except:
                    pass
            elif config.llm_backend == "groq":
                config.groqApi_key = dialog.api_key()
                try:
                    check = eval(config.groqApi_key)
                    if isinstance(check, list):
                        config.groqApi_key = check
                except:
                    pass
            elif config.llm_backend == "github":
                config.githubApi_key = dialog.api_key()
                try:
                    check = eval(config.githubApi_key)
                    if isinstance(check, list):
                        config.githubApi_key = check
                except:
                    pass
            os.environ["OPENAI_API_KEY"] = config.openaiApi_key
            #config.openaiApiOrganization = dialog.org()
            try:
                if config.llm_backend in ("openai", "github", "azure"):
                    config.openaiApi_chat_model_max_tokens = int(dialog.max_token())
                    if config.openaiApi_chat_model_max_tokens < 20:
                        config.openaiApi_chat_model_max_tokens = 20
                elif config.llm_backend == "google":
                    config.googleaiApi_chat_model_max_tokens = int(dialog.max_token())
                    if config.googleaiApi_chat_model_max_tokens < 20:
                        config.googleaiApi_chat_model_max_tokens = 20
                elif config.llm_backend == "grok":
                    config.grokApi_chat_model_max_tokens = int(dialog.max_token())
                    if config.grokApi_chat_model_max_tokens < 20:
                        config.grokApi_chat_model_max_tokens = 20
                elif config.llm_backend == "mistral":
                    config.mistralApi_chat_model_max_tokens = int(dialog.max_token())
                    if config.mistralApi_chat_model_max_tokens < 20:
                        config.mistralApi_chat_model_max_tokens = 20
                elif config.llm_backend == "groq":
                    config.groqApi_chat_model_max_tokens = int(dialog.max_token())
                    if config.groqApi_chat_model_max_tokens < 20:
                        config.groqApi_chat_model_max_tokens = 20
            except:
                pass
            try:
                config.chatGPTApiMaximumInternetSearchResults = int(dialog.max_internet_search_results())
                if config.chatGPTApiMaximumInternetSearchResults <= 0:
                    config.chatGPTApiMaximumInternetSearchResults = 1
                elif config.chatGPTApiMaximumInternetSearchResults > 100:
                    config.chatGPTApiMaximumInternetSearchResults = 100
            except:
                pass
            #config.chatGPTApiIncludeDuckDuckGoSearchResults = dialog.include_internet_searches()
            config.chatGPTApiAutoScrolling = dialog.enable_auto_scrolling()
            config.runPythonScriptGlobally = dialog.enable_runPythonScriptGlobally()
            config.chatAfterFunctionCalled = dialog.enable_chatAfterFunctionCalled()
            if config.llm_backend in ("openai", "github", "azure"):
                config.openaiApi_chat_model = dialog.apiModel()
            elif config.llm_backend == "google":
                config.googleaiApi_chat_model = dialog.apiModel()
            elif config.llm_backend == "grok":
                config.grokApi_chat_model = dialog.apiModel()
            elif config.llm_backend == "mistral":
                config.mistralApi_chat_model = dialog.apiModel()
            elif config.llm_backend == "groq":
                config.groqApi_chat_model = dialog.apiModel()
            config.chatApiFunctionCall = dialog.functionCalling()
            config.chatApiLoadingInternetSearches = dialog.loadingInternetSearches()
            internetSeraches = "integrate google searches"
            if config.chatApiLoadingInternetSearches == "auto" and internetSeraches in config.chatGPTPluginExcludeList:
                config.chatGPTPluginExcludeList.remove(internetSeraches)
                self.parent.reloadMenubar()
            elif config.chatApiLoadingInternetSearches == "none" and not internetSeraches in config.chatGPTPluginExcludeList:
                config.chatGPTPluginExcludeList.append(internetSeraches)
                self.parent.reloadMenubar()
            config.mainWindow.runBibleChatPlugins()
            #config.chatGPTApiPredefinedContext = dialog.predefinedContext()
            #config.chatGPTApiContextInAllInputs = dialog.contextInAllInputs()
            config.chatGPTApiContext = dialog.context()
            #config.chatGPTApiAudioLanguage = dialog.language()
            self.newData()

    def updateApiModel(self, index):
        self.apiModel = index

    def updateBackend(self, index):
        if index == 0:
            config.llm_backend = "openai"
        elif index == 1:
            config.llm_backend = "github"
        elif index == 2:
            config.llm_backend = "azure"
        elif index == 3:
            config.llm_backend = "google"
        elif index == 4:
            config.llm_backend = "groq"
        elif index == 5:
            config.llm_backend = "mistral"
        elif index == 6:
            config.llm_backend = "grok"

    def updateTemperature(self, index):
        if config.llm_backend == "mistral":
            config.mistralApi_llmTemperature = float(index / 10)
        elif config.llm_backend == "grok":
            config.grokApi_llmTemperature = float(index / 10)
        elif config.llm_backend == "groq":
            config.groqApi_llmTemperature = float(index / 10)
        elif config.llm_backend in ("openai", "github", "azure"):
            config.openaiApi_llmTemperature = float(index / 10)
        elif config.llm_backend == "google":
            config.googleaiApi_llmTemperature = float(index / 10)

    def updateChoiceNumber(self, index):
        config.chatApiNoOfChoices = index + 1
        self.audioCheckbox.hide() if config.chatApiNoOfChoices == 1 else self.audioCheckbox.show()

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

    def noTextSelection(self):
        self.displayMessage("This feature works on text selection. Select text first!")

    def validate_url(self, url):
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def webBrowse(self, userInput=""):
        if not userInput:
            userInput = self.contentView.textCursor().selectedText().strip()
        if not userInput:
            self.noTextSelection()
            return
        if self.validate_url(userInput):
            url = userInput
        else:
            userInput = urllib.parse.quote(userInput)
            url = f"https://www.google.com/search?q={userInput}"
        webbrowser.open(url)

    def displayText(self, text):
        self.saveData()
        self.newData()
        self.contentView.setPlainText(text)

    def runSystemCommand(self, command=""):
        if not command:
            command = self.contentView.textCursor().selectedText().strip()
        if command:
            # replace line separator
            command = repr(command)
            command = eval(command).replace("\u2029", "\n")
        else:
            self.noTextSelection()
            return

        # display output only, without error
        #output = subprocess.check_output(command, shell=True, text=True)
        #self.displayText(output)

        # display both output and error
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout  # Captured standard output
        error = result.stderr  # Captured standard error
        self.displayText(f"> {command}")
        self.contentView.appendPlainText(f"\n{output}")
        if error.strip():
            self.contentView.appendPlainText("\n# Error\n")
            self.contentView.appendPlainText(error)

    def runPythonCommand(self, command=""):
        if not command:
            command = self.contentView.textCursor().selectedText().strip()
        if command:
            # replace line separator
            command = repr(command)
            command = eval(command).replace("\u2029", "\n")
        else:
            self.noTextSelection()
            return

        # Store the original standard output
        original_stdout = sys.stdout
        # Create a StringIO object to capture the output
        output = StringIO()
        try:
            # Redirect the standard output to the StringIO object
            sys.stdout = output
            # Execute the Python string in global namespace
            try:
                exec(command, globals()) if config.runPythonScriptGlobally else exec(command)
                captured_output = output.getvalue()
            except:
                captured_output = traceback.format_exc()
            # Get the captured output
        finally:
            # Restore the original standard output
            sys.stdout = original_stdout

        # Display the captured output
        if captured_output.strip():
            self.displayText(captured_output)
        else:
            self.displayMessage("Done!")

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
            self.newData()

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

    def bibleChatAction(self, context=""):
        if context:
            config.chatGPTApiPredefinedContext = context
            index = list(config.predefinedContexts).index(context)
            self.predefinedContextBox.setCurrentIndex(index)
        currentSelectedText = self.contentView.textCursor().selectedText().strip()
        if currentSelectedText:
            self.newData()
            self.userInput.setText(currentSelectedText)
            self.sendMessage()

    def newData(self):
        if not self.busyLoading:
            self.contentID = ""
            self.contentView.setPlainText("" if isLLMReady() else """API Key NOT Found!

Follow the following steps:
1) Register and get an API key in one of the following websites:
    OpenAI - https://platform.openai.com/account/api-keys
    Github - https://github.com/eliranwong/UniqueBible/wiki/Free-Github-API-Key
    Google - https://ai.google.dev/
    Grok - https://docs.x.ai/docs
    Groq - https://console.groq.com/keys
    Mistral - https://console.mistral.ai/api-keys/
2) Select a backend below
3) Click the "Settings" button, right next to the backend selection combo
4) Enter your own API key for the backend you selected""")
            self.setUserInputFocus()

    def selectData(self, index):
        if not self.busyLoading:
            data = index.data(Qt.UserRole)
            self.contentID = data[0]
            content = data[2]
            self.contentView.setPlainText(content)
            self.setUserInputFocus()

    def printData(self):
        # Get the printer and print dialog
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        # If the user clicked "OK" in the print dialog, print the text
        if dialog.exec() == QPrintDialog.Accepted:
            document = QTextDocument()
            document.setPlainText(self.contentView.toPlainText())
            document.print_(printer)

    def exportData(self):
        # Show a file dialog to get the file path to save
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filePath, _ = QFileDialog.getSaveFileName(self, "Export Chat Content", os.path.join(os.path.abspath(config.marvelData), "chats", "chat.txt"), "Text Files (*.txt);;Python Files (*.py);;All Files (*)", options=options)

        # If the user selects a file path, save the file
        if filePath:
            with open(filePath, "w", encoding="utf-8") as fileObj:
                fileObj.write(self.contentView.toPlainText().strip())

    def openTextFileDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      "Open Text File",
                                                      "Text File",
                                                      "Plain Text Files (*.txt);;Python Scripts (*.py);;All Files (*)",
                                                      "", options)
        if fileName:
            with open(fileName, "r", encoding="utf-8") as fileObj:
                self.displayText(fileObj.read())

    def displayMessage(self, message="", title="ChatGPT-GUI"):
        QMessageBox.information(self, title, message)

    # The following method was modified from source:
    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    def num_tokens_from_messages(self, model=""):
        if not model:
            model = config.openaiApi_chat_model
        userInput = self.userInput.text().strip()
        messages = self.getMessages(userInput)

        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        #encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            #print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            #print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        #return num_tokens
        self.displayMessage(message=f"{num_tokens} prompt tokens counted!")

    def getContext(self):
        if not config.chatGPTApiPredefinedContext in config.predefinedContexts:
            config.chatGPTApiPredefinedContext = "[none]"
        if config.chatGPTApiPredefinedContext == "[none]":
            # no context
            context = ""
        elif config.chatGPTApiPredefinedContext == "[custom]":
            # custom input in the settings dialog
            context = config.chatGPTApiContext
        else:
            # users can modify config.predefinedContexts via plugins
            context = config.predefinedContexts[config.chatGPTApiPredefinedContext]
            # change configs for particular contexts
            if config.chatGPTApiPredefinedContext == "Execute Python Code":
                if config.chatApiFunctionCall == "none":
                    config.chatApiFunctionCall = "auto"
                if config.chatApiLoadingInternetSearches == "always":
                    config.chatApiLoadingInternetSearches = "auto"
        return context

    def getMessages(self, userInput):
        # system message
        systemMessage = config.bibleChat_systemMessage
        #if config.chatApiFunctionCall == "auto" and config.chatGPTApiFunctionSignatures:
        #    systemMessage += " Only use the functions you have been provided with."
        messages = [
            {"role": "system", "content": systemMessage}
        ]
        # predefined context
        context = self.getContext()
        # chat history
        history = self.contentView.toPlainText().strip()
        if history:
            if context and not config.chatGPTApiPredefinedContext == "Execute Python Code" and not config.chatGPTApiContextInAllInputs:
                messages.append({"role": "assistant", "content": context})
            if history.startswith(">>> "):
                history = history[4:]
            exchanges = [exchange for exchange in history.split("\n>>> ") if exchange.strip()]
            for exchange in exchanges:
                qa = exchange.split("\n~~~ ")
                for i, content in enumerate(qa):
                    if i == 0:
                        messages.append({"role": "user", "content": content.strip()})
                    else:
                        messages.append({"role": "assistant", "content": content.strip()})
        # customise chat context
        if context and (config.chatGPTApiPredefinedContext == "Execute Python Code" or (not history or (history and config.chatGPTApiContextInAllInputs))):
            #messages.append({"role": "assistant", "content": context})
            userInput = f"{context}\n{userInput}"
        # user input
        messages.append({"role": "user", "content": userInput})
        return messages

    def print(self, text):
        if not config.chatGPTApiPredefinedContext == "[none]":
            text += " (" + config.chatGPTApiPredefinedContext + ")"
        self.contentView.appendPlainText(f"\n{text}" if self.contentView.toPlainText() else text)
        self.contentView.setPlainText(re.sub("\n\n[\n]+?([^\n])", r"\n\n\1", self.contentView.toPlainText()))

    def printStream(self, text):
        # transform responses
        for t in config.chatGPTTransformers:
            text = t(text)
        self.contentView.setPlainText(self.contentView.toPlainText() + text)
        # no audio for streaming tokens
        #if config.chatGPTApiAudio:
        #    self.playAudio(text)
        # scroll to the bottom
        if config.chatGPTApiAutoScrolling:
            contentScrollBar = self.contentView.verticalScrollBar()
            contentScrollBar.setValue(contentScrollBar.maximum())

    def sendMessage(self):
        userInput = self.userInput.text().strip()
        if not userInput in self.recentCommands:
            self.recentCommands.append(userInput)
            completer = QCompleter(self.recentCommands + config.inputSuggestions)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.userInput.setCompleter(completer)
        if self.userInputMultiline.isVisible():
            self.multilineButtonClicked()
        if self.apiModel == 0:
            self.getResponse()
        elif self.apiModel == 1:
            self.getImage()
        elif self.apiModel == 2:
            if userInput:
                self.webBrowse(userInput)
        elif self.apiModel == 3:
            if userInput:
                self.runPythonCommand(userInput)
        elif self.apiModel == 4:
            if userInput:
                self.runSystemCommand(userInput)

    def getImage(self):
        if not self.progressBar.isVisible():
            userInput = self.userInput.text().strip()
            if userInput:
                self.userInput.setDisabled(True)
                self.progressBar.show() # show progress bar
                OpenAIImage(self).workOnGetResponse(userInput)

    def displayImage(self, imageUrl):
        if imageUrl:
            webbrowser.open(imageUrl)
            self.userInput.setEnabled(True)
            self.progressBar.hide()

    def getResponse(self):
        if self.progressBar.isVisible() and config.chatApiNoOfChoices == 1:
            stop_file = ".stop_chatgpt"
            if not os.path.isfile(stop_file):
                open(stop_file, "a", encoding="utf-8").close()
        elif not self.progressBar.isVisible():
            userInput = self.userInput.text().strip()
            if userInput:
                self.userInput.setDisabled(True)
                if config.chatApiNoOfChoices == 1:
                    self.sendButton.setText(config.thisTranslation["stop"])
                    self.busyLoading = True
                    self.listView.setDisabled(True)
                    self.newButton.setDisabled(True)
                messages = self.getMessages(userInput)
                self.print(f">>> {userInput}")
                self.saveData()
                self.currentLoadingID = self.contentID
                self.currentLoadingContent = self.contentView.toPlainText().strip()
                self.progressBar.show() # show progress bar
                ChatGPTResponse(self).workOnGetResponse(messages) # get chatGPT response in a separate thread

    def processResponse(self, responses):
        if responses:
            # reload the working content in case users change it during waiting for response
            self.contentID = self.currentLoadingID
            self.contentView.setPlainText(self.currentLoadingContent)
            self.currentLoadingID = self.currentLoadingContent = ""
            # transform responses
            for t in config.chatGPTTransformers:
                responses = t(responses)
            # update new reponses
            self.print(responses)
            # scroll to the bottom
            if config.chatGPTApiAutoScrolling:
                contentScrollBar = self.contentView.verticalScrollBar()
                contentScrollBar.setValue(contentScrollBar.maximum())
        # empty user input
        self.userInput.setText("")
        # auto-save
        self.saveData()
        # hide progress bar
        self.userInput.setEnabled(True)
        if config.chatApiNoOfChoices == 1:
            self.listView.setEnabled(True)
            self.newButton.setEnabled(True)
            self.busyLoading = False
        self.sendButton.setText(config.thisTranslation["send"])
        self.progressBar.hide()
        self.setUserInputFocus()

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

    def reloadMenubar(self):
        self.menuBar().clear()
        self.createMenubar()

    def createMenubar(self):
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

        new_action = QAction(config.thisTranslation["databaseDirectory"], self)
        new_action.triggered.connect(self.openDatabaseDirectory)
        file_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["pluginDirectory"], self)
        new_action.triggered.connect(self.openPluginsDirectory)
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

        new_action = QAction(config.thisTranslation["exportChat"], self)
        new_action.triggered.connect(self.chatGPT.exportData)
        file_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["printChat"], self)
        new_action.setShortcut("Ctrl+P")
        new_action.triggered.connect(self.chatGPT.printData)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction(config.thisTranslation["readTextFile"], self)
        new_action.triggered.connect(self.chatGPT.openTextFileDialog)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction(config.thisTranslation["countPromptTokens"], self)
        new_action.triggered.connect(self.chatGPT.num_tokens_from_messages)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Create a Exit action and add it to the File menu
        exit_action = QAction(config.thisTranslation["exit"], self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Create customise menu
        customise_menu = menubar.addMenu(config.thisTranslation["customise"])

        openSettings = QAction(config.thisTranslation["chatSettings"], self)
        openSettings.triggered.connect(self.chatGPT.showApiDialog)
        customise_menu.addAction(openSettings)

        new_action = QAction(config.thisTranslation["toggleMultilineInput"], self)
        new_action.setShortcut("Ctrl+L")
        new_action.triggered.connect(self.chatGPT.multilineButtonClicked)
        customise_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["toggleRegexp"], self)
        new_action.setShortcut("Ctrl+E")
        new_action.triggered.connect(self.toggleRegexp)
        customise_menu.addAction(new_action)

        # Create predefined context menu
        context_menu = menubar.addMenu(config.thisTranslation["predefinedContext"])
        for index, context in enumerate(config.predefinedContexts):
            contextAction = QAction(context, self)
            if index < 10:
                contextAction.setShortcut(f"Ctrl+{index}")
            contextAction.triggered.connect(partial(self.chatGPT.bibleChatAction, context))
            context_menu.addAction(contextAction)

        # Create a plugin menu
        plugin_menu = menubar.addMenu(config.thisTranslation["plugins"])

        pluginFolder = os.path.join(config.packageDir, "plugins", "chatGPT")
        for index, plugin in enumerate(FileUtil.fileNamesWithoutExtension(pluginFolder, "py")):
            new_action = QAction(plugin, self)
            new_action.setCheckable(True)
            new_action.setChecked(False if plugin in config.chatGPTPluginExcludeList else True)
            new_action.triggered.connect(partial(self.updateExcludePluginList, plugin))
            plugin_menu.addAction(new_action)

        # Create a text selection menu
        text_selection_menu = menubar.addMenu(config.thisTranslation["textSelection"])

        new_action = QAction(config.thisTranslation["webBrowser"], self)
        new_action.triggered.connect(self.chatGPT.webBrowse)
        text_selection_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["runAsPythonCommand"], self)
        new_action.triggered.connect(self.chatGPT.runPythonCommand)
        text_selection_menu.addAction(new_action)

        new_action = QAction(config.thisTranslation["runAsSystemCommand"], self)
        new_action.triggered.connect(self.chatGPT.runSystemCommand)
        text_selection_menu.addAction(new_action)


        # Create a about menu
        about_menu = menubar.addMenu(config.thisTranslation["about"])

        openSettings = QAction(config.thisTranslation["repository"], self)
        openSettings.triggered.connect(lambda: webbrowser.open("https://github.com/eliranwong/ChatGPT-GUI"))
        about_menu.addAction(openSettings)

        about_menu.addSeparator()

        new_action = QAction(config.thisTranslation["help"], self)
        new_action.triggered.connect(lambda: webbrowser.open("https://github.com/eliranwong/ChatGPT-GUI/wiki"))
        about_menu.addAction(new_action)

        about_menu.addSeparator()

        new_action = QAction(config.thisTranslation["donate"], self)
        new_action.triggered.connect(lambda: webbrowser.open("https://www.paypal.com/paypalme/MarvelBible"))
        about_menu.addAction(new_action)

    def initUI(self):
        # Set a central widget
        self.chatGPT = ChatGPTAPI(self)
        self.setCentralWidget(self.chatGPT)

        # create menu bar
        self.createMenubar()

        # set initial window size
        #self.setWindowTitle("Bible Chat")
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
        self.show()
        self.chatGPT.setFontSize()

    def updateExcludePluginList(self, plugin):
        if plugin in config.chatGPTPluginExcludeList:
            config.chatGPTPluginExcludeList.remove(plugin)
        else:
            config.chatGPTPluginExcludeList.append(plugin)
        internetSeraches = "integrate google searches"
        if internetSeraches in config.chatGPTPluginExcludeList and config.chatApiLoadingInternetSearches == "auto":
            config.chatApiLoadingInternetSearches = "none"
        elif not internetSeraches in config.chatGPTPluginExcludeList and config.chatApiLoadingInternetSearches == "none":
            config.chatApiLoadingInternetSearches = "auto"
            config.chatApiFunctionCall = "auto"
        # reload plugins
        config.mainWindow.runBibleChatPlugins()

    def getOpenCommand(self):
        thisOS = platform.system()
        if thisOS == "Windows":
            openCommand = "start"
        elif thisOS == "Darwin":
            openCommand = "open"
        elif thisOS == "Linux":
            openCommand = "xdg-open"
        return openCommand

    def openDatabaseDirectory(self):
        databaseDirectory = os.path.dirname(os.path.abspath(config.chatGPTApiLastChatDatabase))
        openCommand = self.getOpenCommand()
        os.system(f"{openCommand} {databaseDirectory}")

    def openPluginsDirectory(self):
        openCommand = self.getOpenCommand()
        os.system(f"{openCommand} plugins")

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

#if isLLMReady():
if config.bibleChatEntry:
    bibleChat.chatGPT.userInput.setText(config.bibleChatEntry)
    bibleChat.chatGPT.sendMessage()
    config.bibleChatEntry = ""
else:
    # load selected text, if any, to user input
    selectedText = config.mainWindow.selectedText()
    if selectedText:
        bibleChat.chatGPT.userInput.setText(selectedText)
        if "\n" in selectedText:
            bibleChat.chatGPT.multilineButtonClicked()