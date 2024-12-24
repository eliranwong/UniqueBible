from uniquebible import config
import sys, traceback, os, platform, openai, json, re, textwrap
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
else:
    from qtpy.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from pydub import AudioSegment
from pydub.playback import play
from uniquebible.util.VlcUtil import VlcUtil
from openai import OpenAI, AzureOpenAI
from mistralai import Mistral
from groq import Groq


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(str)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # assign a reference to this current thread
        #config.workerThread = QThread.currentThread()

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class ChatGPTResponse:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def fineTunePythonCode(self, code):
        insert_string = "from uniquebible import config\nconfig.pythonFunctionResponse = "
        code = re.sub("^!(.*?)$", r"import os\nos.system(\1)", code, flags=re.M)
        if "\n" in code:
            substrings = code.rsplit("\n", 1)
            lastLine = re.sub("print\((.*)\)", r"\1", substrings[-1])
            code = code if lastLine.startswith(" ") else f"{substrings[0]}\n{insert_string}{lastLine}"
        else:
            code = f"{insert_string}{code}"
        return code

    def getFunctionResponse(self, response_message, function_name):
        if function_name == "python":
            config.pythonFunctionResponse = ""
            python_code = textwrap.dedent(response_message["function_call"]["arguments"])
            refinedCode = self.fineTunePythonCode(python_code)

            print("--------------------")
            print(f"running python code ...")
            if config.developer or config.codeDisplay:
                print("```")
                print(python_code)
                print("```")
            print("--------------------")

            try:
                exec(refinedCode, globals())
                function_response = str(config.pythonFunctionResponse)
            except:
                function_response = python_code
            info = {"information": function_response}
            function_response = json.dumps(info)
        else:
            fuction_to_call = config.chatGPTApiAvailableFunctions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = fuction_to_call(function_args)
        return function_response

    def getStreamFunctionResponseMessage(self, completion, function_name):
        function_arguments = ""
        for event in completion:
            delta = event["choices"][0]["delta"]
            if delta and delta.get("function_call"):
                function_arguments += delta["function_call"]["arguments"]
        return {
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": function_arguments,
            }
        }

    def runCompletion(self, thisMessage, progress_callback):

        def getGroqApi_key():
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
        def getGithubApi_key():
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
        def getMistralApi_key():
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

        self.functionJustCalled = True
        if config.llm_backend == "google":
            # https://ai.google.dev/gemini-api/docs/openai
            googleaiClient = OpenAI(
                api_key=config.googleaiApi_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            return googleaiClient.chat.completions.create(
                model=config.googleaiApi_chat_model,
                messages=thisMessage,
                n=1,
                temperature=config.googleaiApi_llmTemperature,
                max_tokens=config.googleaiApi_chat_model_max_tokens,
                stream=True,
            )
        elif config.llm_backend == "grok":
            grokClient = OpenAI(
                api_key=config.grokApi_key,
                base_url="https://api.x.ai/v1",
            )
            return grokClient.chat.completions.create(
                model=config.grokApi_chat_model,
                messages=thisMessage,
                n=1,
                temperature=config.grokApi_llmTemperature,
                max_tokens=config.grokApi_chat_model_max_tokens,
                stream=True,
            )
        elif config.llm_backend == "mistral":
            return Mistral(api_key=getMistralApi_key()).chat.stream(
                model=config.mistralApi_chat_model,
                messages=thisMessage,
                n=1,
                temperature=config.mistralApi_llmTemperature,
                max_tokens=config.mistralApi_chat_model_max_tokens,
            )
        elif config.llm_backend == "openai":
            if not config.openaiApi_key:
                return None
            os.environ["OPENAI_API_KEY"] = config.openaiApi_key
            return OpenAI().chat.completions.create(
                model=config.openaiApi_chat_model,
                messages=thisMessage,
                n=1,
                temperature=config.openaiApi_llmTemperature,
                max_tokens=config.openaiApi_chat_model_max_tokens,
                stream=True,
            )
        elif config.llm_backend == "azure":
            # azure_endpoint should be something like https://<your-resource-name>.openai.azure.com without "/models" at the end
            endpoint = re.sub("/models[/]*$", "", config.azureBaseUrl)
            azureClient = AzureOpenAI(azure_endpoint=endpoint,api_version=config.azure_api_version,api_key=config.azureApi_key)
            return azureClient.chat.completions.create(
                model=config.openaiApi_chat_model,
                messages=thisMessage,
                n=1,
                temperature=config.openaiApi_llmTemperature,
                max_tokens=config.openaiApi_chat_model_max_tokens,
                stream=True,
            )
        elif config.llm_backend == "github":
            githubClient = OpenAI(
                api_key=getGithubApi_key(),
                base_url="https://models.inference.ai.azure.com",
            )
            return githubClient.chat.completions.create(
                model=config.openaiApi_chat_model,
                messages=thisMessage,
                n=1,
                temperature=config.openaiApi_llmTemperature,
                max_tokens=config.openaiApi_chat_model_max_tokens,
                stream=True,
            )
        if not config.groqApi_key:
            return None
        return Groq(api_key=getGroqApi_key()).chat.completions.create(
            model=config.groqApi_chat_model,
            messages=thisMessage,
            n=1,
            temperature=config.groqApi_llmTemperature,
            max_tokens=config.groqApi_chat_model_max_tokens,
            stream=True,
        )

    def showErrors(self):
        if config.developer:
            print(traceback.format_exc())

    def getResponse(self, messages, progress_callback, functionJustCalled=False):
        responses = ""
        if config.chatApiLoadingInternetSearches == "always" and not functionJustCalled:
            #print("loading internet searches ...")
            try:
                completion = openai.ChatCompletion.create(
                    model=config.openaiApi_chat_model,
                    messages=messages,
                    max_tokens=config.openaiApi_chat_model_max_tokens,
                    temperature=config.openaiApi_llmTemperature,
                    n=1,
                    functions=config.integrate_google_searches_signature,
                    function_call={"name": "integrate_google_searches"},
                )
                response_message = completion["choices"][0]["message"]
                if response_message.get("function_call"):
                    function_args = json.loads(response_message["function_call"]["arguments"])
                    fuction_to_call = config.chatGPTApiAvailableFunctions.get("integrate_google_searches")
                    function_response = fuction_to_call(function_args)
                    messages.append(response_message) # extend conversation with assistant's reply
                    messages.append(
                        {
                            "role": "function",
                            "name": "integrate_google_searches",
                            "content": function_response,
                        }
                    )
            except:
                print("Unable to load internet resources.")
        try:
            if config.chatApiNoOfChoices == 1: ## change: this is the only option the latest code support, to simply the use of ai chat, use toolmate.ai for additional features
                completion = self.runCompletion(messages, progress_callback)
                if completion is not None:
                    progress_callback.emit("\n\n~~~ ")
                    for event in completion:
                        # stop generating response
                        stop_file = ".stop_chatgpt"
                        if os.path.isfile(stop_file):
                            os.remove(stop_file)
                            break                                 
                        # RETRIEVE THE TEXT FROM THE RESPONSE
                        if isinstance(event, str):
                            progress = event
                        elif hasattr(event, "data"): # mistralai
                            progress = event.data.choices[0].delta.content
                        elif not event.choices: # in case of the first event of Azure completion
                            continue
                        else:
                            progress = event.choices[0].delta.content
                        # STREAM THE ANSWER
                        progress_callback.emit(progress)
            else:
                if config.chatGPTApiFunctionSignatures:
                    completion = openai.ChatCompletion.create(
                        model=config.openaiApi_chat_model,
                        messages=messages,
                        max_tokens=config.openaiApi_chat_model_max_tokens,
                        temperature=0.0 if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.openaiApi_llmTemperature,
                        n=config.chatApiNoOfChoices,
                        functions=config.chatGPTApiFunctionSignatures,
                        function_call={"name": "run_python"} if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatApiFunctionCall,
                    )
                else:
                    completion = openai.ChatCompletion.create(
                        model=config.openaiApi_chat_model,
                        messages=messages,
                        max_tokens=config.openaiApi_chat_model_max_tokens,
                        temperature=config.openaiApi_llmTemperature,
                        n=config.chatApiNoOfChoices,
                    )

                response_message = completion["choices"][0]["message"]
                if response_message.get("function_call"):
                    function_name = response_message["function_call"]["name"]
                    if function_name == "python":
                        config.pythonFunctionResponse = ""
                        function_args = response_message["function_call"]["arguments"]
                        insert_string = "from uniquebible import config\nconfig.pythonFunctionResponse = "
                        if "\n" in function_args:
                            substrings = function_args.rsplit("\n", 1)
                            new_function_args = f"{substrings[0]}\n{insert_string}{substrings[-1]}"
                        else:
                            new_function_args = f"{insert_string}{function_args}"
                        try:
                            exec(new_function_args, globals())
                            function_response = str(config.pythonFunctionResponse)
                        except:
                            function_response = function_args
                        info = {"information": function_response}
                        function_response = json.dumps(info)
                    else:
                        #if not function_name in config.chatGPTApiAvailableFunctions:
                        #    print("unexpected function name: ", function_name)
                        fuction_to_call = config.chatGPTApiAvailableFunctions.get(function_name, "integrate_google_searches")
                        try:
                            function_args = json.loads(response_message["function_call"]["arguments"])
                        except:
                            function_args = response_message["function_call"]["arguments"]
                            if function_name == "integrate_google_searches":
                                function_args = {"keywords": function_args}
                        function_response = fuction_to_call(function_args)

                    # check function response
                    # print("Got this function response:", function_response)

                    # process function response
                    # send the info on the function call and function response to GPT
                    messages.append(response_message) # extend conversation with assistant's reply
                    messages.append(
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        }
                    )  # extend conversation with function response
                    if config.chatAfterFunctionCalled:
                        return self.getResponse(messages, progress_callback, functionJustCalled=True)
                    else:
                        responses += f"{function_response}\n\n"

                for index, choice in enumerate(completion.choices):
                    chat_response = choice.message.content
                    if chat_response:
                        if len(completion.choices) > 1:
                            if index > 0:
                                responses += "\n"
                            responses += f"~~~ Response {(index+1)}:\n"
                        responses += f"{chat_response}\n\n"
        except:
            responses = traceback.format_exc()
        return responses

    def workOnGetResponse(self, messages):
        # Pass the function to execute
        worker = Worker(self.getResponse, messages) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.parent.processResponse)
        worker.signals.progress.connect(self.parent.printStream)
        # Connection
        #worker.signals.finished.connect(None)
        # Execute
        self.threadpool.start(worker)


class OpenAIImage:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def getResponse(self, prompt, progress_callback=None):
        try:
            #https://platform.openai.com/docs/guides/images/introduction
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
        # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
        except openai.error.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            print(f"OpenAI API request exceeded rate limit: {e}")
        except:
            traceback.print_exc()
        return response['data'][0]['url']

    def workOnGetResponse(self, prompt):
        # Pass the function to execute
        worker = Worker(self.getResponse, prompt) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.parent.displayImage)
        # Connection
        #worker.signals.finished.connect(None)
        # Execute
        self.threadpool.start(worker)


class VLCVideo:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def playVideo(self, videoFilePath, speed, progress_callback=None):
        VlcUtil.playMediaFile(videoFilePath, speed)
        return "Next ..."

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def workOnPlayVideo(self, videoFilePath, speed):
        # Pass the function to execute
        worker = Worker(self.playVideo, videoFilePath, speed) # Any other args, kwargs are passed to the run function
        worker.signals.finished.connect(self.parent.workOnPlaylistIndex)
        #worker.signals.result.connect(self.print_output)
        #worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)


class YouTubeDownloader:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def downloadYouTubeFile(self, downloadCommand, youTubeLink, outputFolder, progress_callback=None):
        try:
            if platform.system() == "Windows":
                os.system(r"cd .\{2}\ & {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
            else:
                os.system(r"cd {2}; {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
            os.system(r"{0} {1}".format(config.openLinuxDirectory if platform.system() == "Linux" else config.open, outputFolder))
        except:
            self.parent.displayMessage(config.thisTranslation["noSupportedUrlFormat"], title="ERROR:")
            return config.thisTranslation["noSupportedUrlFormat"]
        return "Downloaded!"

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def workOnDownloadYouTubeFile(self, downloadCommand, youTubeLink, outputFolder):
        # Pass the function to execute
        worker = Worker(self.downloadYouTubeFile, downloadCommand, youTubeLink, outputFolder) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(lambda: self.parent.reloadResources())
        #worker.signals.finished.connect(self.parent.reloadResources)
        # Execute
        self.threadpool.start(worker)

class PydubAudio:

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.threadpool = QThreadPool()

    def pydubFile(self, progress_callback=None):
        # vlc gui for video only
        config.isMediaPlaying = True
        # Load audio file
        audio = AudioSegment.from_file(config.currentAudioFile, format="mp3")
        # Change speed
        faster_audio = audio.speedup(playback_speed=1.5)
        # Change volume
        louder_audio = faster_audio + 10
        # Play audio
        config.playback = play(louder_audio)

        config.isMediaPlaying = False
        return "Finished Playing!"

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def workOnPydubFile(self):
        # Pass the function to execute
        worker = Worker(self.pydubFile) # Any other args, kwargs are passed to the run function
        #worker.signals.result.connect(self.print_output)
        #worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)
        
    # stop https://stackoverflow.com/questions/47596007/stop-the-audio-from-playing-in-pydub