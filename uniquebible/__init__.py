import os, requests, re, socket
import importlib.metadata
from shutil import copy, copytree
from pathlib import Path
from packaging import version
from uniquebible import config


# go to resource directory
thisFile = os.path.realpath(__file__)
config.packageDir = os.path.dirname(thisFile)

ubahome = os.path.expanduser(os.path.join("~", "UniqueBible"))

# restor previous backup
configFile = os.path.join(config.packageDir, "config.py")
backupFile = os.path.join(ubahome, "config.py.bk")
if os.path.isfile(backupFile) and not hasattr(config, "mainText"):
    print(f"Configuration backup found: {backupFile}")
    try:
        print("Loading backup ...")
        with open(backupFile, "r", encoding="utf-8") as fileObj:
            configs = fileObj.read()
        # load backup configs
        configs = "from uniquebible import config\n" + re.sub("^([A-Za-z0-9])", r"config.\1", configs, flags=re.M)
        exec(configs, globals())
        # copy backup configs
        copy(backupFile, configFile)
        config.enabled = []
        print("Previous configurations restored!")
    except:
        try:
            os.rename(backupFile, f"{backupFile}_failed")
        except:
            pass
        print("Failed to restore previous configurations!")

# set up folders for storing user content in ~/UniqueBible
if not os.path.isdir(ubahome):
    Path(ubahome).mkdir(parents=True, exist_ok=True)
for i in ("audio", "htmlResources", "import", "macros", "marvelData", "music", "notes", "temp", "terminal_history", "terminal_mode", "thirdParty", "video", "webstorage", "workspace"):
    sourceFolder = os.path.join(config.packageDir, i)
    targetFolder = os.path.join(ubahome, i)
    if not os.path.isdir(targetFolder):
        print(f"Setting up user directory '{i}' ...")
        copytree(sourceFolder, targetFolder, dirs_exist_ok=True)
    #copytree(i, os.path.join(ubahome, i), dirs_exist_ok=True)

# set up map images
import uniquebible.htmlResources.images.exlbl
import uniquebible.htmlResources.images.exlbl_large
import uniquebible.htmlResources.images.exlbl_largeHD_1
import uniquebible.htmlResources.images.exlbl_largeHD_2
import uniquebible.htmlResources.images.exlbl_largeHD_3

# Add folders below for all new folders created after version 0.1.17
# ...

# change directory to user directory
if os.getcwd() != ubahome:
    os.chdir(ubahome)

# user plugins; create folders for users to place their own plugins
# TODO: user plugins not working for now; will implement later
for i in ("chatGPT", "config", "context", "event", "language", "layout", "menu", "shutdown", "startup", "terminal", "text_editor"):
    Path(os.path.join(ubahome, "plugins", i)).mkdir(parents=True, exist_ok=True)

def getSitePackagesLocation():
    return os.path.dirname(config.packageDir)

def getPackageInstalledVersion(package):
    try:
        installed_version = importlib.metadata.version(package)
        return version.parse(installed_version)
    except:
        return None

def getPackageLatestVersion(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
        latest_version = response.json()['info']['version']
        return version.parse(latest_version)
    except:
        return None

def isServerAlive(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Timeout in case of server not responding
    try:
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False

if hasattr(config, "checkVersionOnStartup") and config.checkVersionOnStartup:

    if isServerAlive("8.8.8.8", 53):

        thisPackage = "uniquebible"

        content = []

        content.append(f"# Checked '{thisPackage}' version ...")

        config.version = installed_version = getPackageInstalledVersion(thisPackage)
        if installed_version is not None:
            content.append(f"Installed version: {installed_version}")
            latest_version = getPackageLatestVersion(thisPackage)
            if latest_version is not None:
                content.append(f"Latest version: {latest_version}")
                if latest_version > installed_version:
                    content.append("Run `pip install --upgrade uniquebible` to upgrade!")
                    print("\n".join(content))

        config.internetConnectivity = True
    else:
        config.internetConnectivity = False
        config.version = "0.0.0"

else:
    config.version = "0.0.0"

# AI Features

from openai import OpenAI, AzureOpenAI
from mistralai import Mistral
from groq import Groq
from typing import Optional
from opencc import OpenCC
import unicodedata, traceback, markdown
from uniquebible.util.BibleVerseParser import BibleVerseParser

config.llm_backends = ["openai", "github", "azure", "google", "grok", "groq", "mistral"]
# check latest version of azure api at https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
config.azure_api_version = "2024-10-21"

def is_CJK(text):
    for char in text:
        if 'CJK' in unicodedata.name(char):
            return True
    return False

def isLLMReady(backend=""):
    if not backend:
        backend = config.llm_backend
    if backend == "openai" and config.openaiApi_key:
        return True
    elif backend == "github" and config.githubApi_key:
        return True
    elif backend == "azure" and config.azureApi_key:
        return True
    elif backend == "mistral" and config.mistralApi_key:
        return True
    elif backend == "grok" and config.grokApi_key:
        return True
    elif backend == "groq" and config.groqApi_key:
        return True
    elif backend == "google" and config.googleaiApi_key:
        return True
    return False

def getGithubApi_key() -> str:
    '''
    support multiple github api keys
    User can manually edit config to change the value of config.githubApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.githubApi_key:
        if isinstance(config.githubApi_key, str):
            return config.githubApi_key
        elif isinstance(config.githubApi_key, list):
            if len(config.githubApi_key) > 1:
                # rotate multiple api keys
                config.githubApi_key = config.githubApi_key[1:] + [config.githubApi_key[0]]
            return config.githubApi_key[0]
        else:
            return ""
    else:
        return ""

def getGroqApi_key() -> str:
    '''
    support multiple grop api keys
    User can manually edit config to change the value of config.groqApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.groqApi_key:
        if isinstance(config.groqApi_key, str):
            return config.groqApi_key
        elif isinstance(config.groqApi_key, list):
            if len(config.groqApi_key) > 1:
                # rotate multiple api keys
                config.groqApi_key = config.groqApi_key[1:] + [config.groqApi_key[0]]
            return config.groqApi_key[0]
        else:
            return ""
    else:
        return ""

def getMistralApi_key() -> str:
    '''
    support multiple mistral api keys
    User can manually edit config to change the value of config.mistralApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.mistralApi_key:
        if isinstance(config.mistralApi_key, str):
            return config.mistralApi_key
        elif isinstance(config.mistralApi_key, list):
            if len(config.mistralApi_key) > 1:
                # rotate multiple api keys
                config.mistralApi_key = config.mistralApi_key[1:] + [config.mistralApi_key[0]]
            return config.mistralApi_key[0]
        else:
            return ""
    else:
        return ""

def getOpenAIClient():
    # priority in order: azure > github > openai
    if config.azureApi_key:
        return AzureOpenAI(azure_endpoint=re.sub("/models[/]*$", "", config.azureBaseUrl),api_version=config.azure_api_version,api_key=config.azureApi_key)
    if config.githubApi_key:
        return OpenAI(api_key=getGithubApi_key(),base_url="https://models.inference.ai.azure.com")
    return OpenAI()

def extract_text(filepath):
    try:
        from markitdown import MarkItDown
        filepath = filepath.rstrip()
        if os.path.isfile(filepath):
            if re.search("(\.jpg|\.jpeg|\.png)$", filepath.lower()):
                md = MarkItDown(llm_client=getOpenAIClient(), llm_model="gpt-4o")
            else:
                md = MarkItDown()
            return md.convert(filepath)
    except:
        return "Install markitdown first!"

def getChatResponse(backend, chatMessages) -> Optional[str]:
    if not isLLMReady(backend) or not backend in config.llm_backends:
        return None
    if config.rawOutput and hasattr(config, "webHomePage") and not config.webHomePage==f"{config.webPrivateHomePage}.html":
        # AI features via web API are accessible to private data users only in http-server mode
        return None
    if not backend == config.llm_backend and hasattr(config, "webHomePage") and not config.webHomePage==f"{config.webPrivateHomePage}.html":
        # Inference with non-default AI backends is accessible to private data users only in http-server mode
        return None
    try:
        if backend == "mistral":
            completion = Mistral(api_key=getMistralApi_key()).chat.complete(
                model=config.mistralApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.mistralApi_llmTemperature,
                max_tokens=config.mistralApi_chat_model_max_tokens,
                stream=False,
            )
        elif backend == "openai":
            os.environ["OPENAI_API_KEY"] = config.openaiApi_key
            completion = OpenAI().chat.completions.create(
                model=config.openaiApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.openaiApi_llmTemperature,
                max_tokens=config.openaiApi_chat_model_max_tokens,
                stream=False,
            )
        elif backend == "github":
            githubClient = OpenAI(
                api_key=getGithubApi_key(),
                base_url="https://models.inference.ai.azure.com",
            )
            completion = githubClient.chat.completions.create(
                model=config.openaiApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.openaiApi_llmTemperature,
                max_tokens=config.openaiApi_chat_model_max_tokens,
                stream=False,
            )
        elif backend == "azure":
            # azure_endpoint should be something like https://<your-resource-name>.openai.azure.com without "/models" at the end
            endpoint = re.sub("/models[/]*$", "", config.azureBaseUrl)
            azureClient = AzureOpenAI(azure_endpoint=endpoint,api_version=config.azure_api_version,api_key=config.azureApi_key)
            completion = azureClient.chat.completions.create(
                model=config.openaiApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.openaiApi_llmTemperature,
                max_tokens=config.openaiApi_chat_model_max_tokens,
                stream=False,
            )
        elif backend == "grok":
            grokClient = OpenAI(
                api_key=config.grokApi_key,
                base_url="https://api.x.ai/v1",
            )
            completion = grokClient.chat.completions.create(
                model=config.grokApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.grokApi_llmTemperature,
                max_tokens=config.grokApi_chat_model_max_tokens,
                stream=False,
            )
        elif backend == "google":
            # https://ai.google.dev/gemini-api/docs/openai
            googleaiClient = OpenAI(
                api_key=config.googleaiApi_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            completion = googleaiClient.chat.completions.create(
                model=config.googleaiApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.googleaiApi_llmTemperature,
                max_tokens=config.googleaiApi_chat_model_max_tokens,
                stream=False,
            )
        else:
            completion = Groq(api_key=getGroqApi_key()).chat.completions.create(
                model=config.groqApi_chat_model,
                messages=chatMessages,
                n=1,
                temperature=config.groqApi_llmTemperature,
                max_tokens=config.groqApi_chat_model_max_tokens,
                stream=False,
            )
        textOutput = completion.choices[0].message.content
        # update the message chain in the config, to work with command `chat`
        config.chatMessages = chatMessages
        config.chatMessages.append({"role": "assistant", "content": textOutput})
    except:
        textOutput = "Failed to connect! Please try again later."
    if hasattr(config, "displayLanguage") and config.displayLanguage == "zh_HANT":
        textOutput = OpenCC('s2t').convert(textOutput)
    elif hasattr(config, "displayLanguage") and config.displayLanguage == "zh_HANS":
        textOutput = OpenCC('t2s').convert(textOutput)
    return textOutput

def getAiFeatureDisclaimer() -> str:
    if config.displayLanguage == "zh_HANT":
        disclaimer = """<hr><p><b>免責聲明：</b> 本網站上由 AI 提供支援的聖經功能旨在提供有關聖經的有用信息和見解。然而，它不能代替個人對經文的學習和反思。聖經本身仍然是基督徒真理和權威的最終來源。請僅將此工具提供的資訊用作參考，並始終查閱聖經以獲得有關您問題的明確答案。</p>"""
    elif config.displayLanguage == "zh_HANS":
        disclaimer = """<hr><p><b>免责声明：</b> 本网站上由 AI 提供支持的圣经功能旨在提供有关圣经的有用信息和见解。然而，它不能代替个人对经文的学习和反思。圣经本身仍然是基督徒真理和权威的最终来源。请仅将此工具提供的信息用作参考，并始终查阅圣经以获得有关您问题的明确答案。</p>"""
    else:
        disclaimer = """<hr><p><b>Disclaimer:</b> The AI-powered Bible feature on this website is intended to provide helpful information and insights about the Bible. However, it is not a substitute for personal study and reflection on the scriptures. The Bible itself remains the ultimate source of truth and authority for Christians. Please use the information provided by this tool for reference only, and always consult the Bible for definitive answers to your questions.</p>"""
    return disclaimer

def showErrors():
    trace = traceback.format_exc()
    print(trace if config.developer else "Error encountered!")
    return trace

def chatContent():
    content = "<h1>AI {0}</h1>".format(config.thisTranslation["chat"])

    if config.chatMessages:
        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        messages = []
        for index, i in enumerate(config.chatMessages):
            iRole = i.get("role", "")
            if not iRole == "system":
                iContent = i.get("content", "")
                if iContent:
                    # add bible reference links
                    iContent = bibleVerseParser.parseText(iContent, splitInChunks=True, parseBooklessReferences=False, canonicalOnly=True)
                    # convert markdown format to html
                    iContent = markdown.markdown(iContent)
                if iRole == "user":
                    color = "#f2f2f2" if config.theme == 'default' else "#5f5f5f"
                    iContent = f'''<p><table style='width: 100%;'><tr style='background-color: {color};'>
                    <td style='vertical-align: text-top;'>{iContent}</td>
                    </tr></table></p>'''
                else:
                    iContent = f'''<p><table style='width: 100%;'><tr>
                    <td style='vertical-align: text-top;'>{iContent}</td>
                    </tr></table></p>'''
                if index == (len(config.chatMessages) - 1):
                    # the last item
                    if config.noQt:
                        iRole = f"""<vid id="v{config.mainB}.{config.mainC}.{config.mainV}"></vid>"""
                    else:
                        iRole = f"""<vid id="v{config.studyB}.{config.studyC}.{config.studyV}"></vid>"""
                messages.append(f'''{iContent}''')
        content += "\n\n".join(messages)

        content += "<hr>"    
    else:
        if config.displayLanguage == "zh_HANT":
            content += """<p>請輸入您的提問，然後按下按鈕「{0}」。</p>""".format(config.thisTranslation["send"])
        elif config.displayLanguage == "zh_HANS":
            content += """<p>请输入您的提问，然后按下按钮「{0}」。</p>""".format(config.thisTranslation["send"])
        else:
            content += """<p>Please enter your query and click the button '{0}'.</p>""".format(config.thisTranslation["send"])

    content += "<p><input type='text' id='chatInput' style='width:95%' autofocus></p>"
    newButton = "" if not config.chatMessages else """ <button id='openChatInputButton' type='button' onclick='document.title="CHAT:::NEW";' class='ubaButton'>{0}</button>""".format(config.thisTranslation["restart"])
    content += """<p><button id='openChatInputButton' type='button' onclick='bibleChat();' class='ubaButton'>{0}</button>{1}</p>""".format(config.thisTranslation["send"], newButton)

    content += getAiFeatureDisclaimer()

    #content = markdown.markdown(content)
    content += """
<script>
function bibleChat() {0}
  var searchString = document.getElementById('chatInput').value;
  document.title = "CHAT:::"+searchString;
{1}
var input = document.getElementById('chatInput');
input.addEventListener('keyup', function(event) {0}
  if (event.keyCode === 13) {0}
   event.preventDefault();
   document.getElementById('openChatInputButton').click();
  {1}
{1});
</script>""".format("{", "}")
    return content