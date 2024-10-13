from uniquebible import config
import sys, traceback, os, platform, openai, json, re, textwrap
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
else:
    from qtpy.QtCore import QRunnable, Slot, Signal, QObject, QThreadPool
from pydub import AudioSegment
from pydub.playback import play
from uniquebible.util.VlcUtil import VlcUtil
from openai import OpenAI


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
        self.functionJustCalled = True
        return OpenAI().chat.completions.create(
            model=config.chatGPTApiModel,
            messages=thisMessage,
            n=1,
            temperature=config.chatGPTApiTemperature,
            max_tokens=config.chatGPTApiMaxTokens,
            stream=True,
        )

    def runCompletion_old(self, thisMessage, progress_callback):
        self.functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            if config.chatGPTApiFunctionSignatures and not self.functionJustCalled:
                return openai.ChatCompletion.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=config.chatGPTApiTemperature,
                    max_tokens=config.chatGPTApiMaxTokens,
                    functions=config.chatGPTApiFunctionSignatures,
                    function_call=config.chatApiFunctionCall,
                    stream=True,
                )
            return openai.ChatCompletion.create(
                model=config.chatGPTApiModel,
                messages=thisThisMessage,
                n=1,
                temperature=config.chatGPTApiTemperature,
                max_tokens=config.chatGPTApiMaxTokens,
                stream=True,
            )

        while True:
            completion = runThisCompletion(thisMessage)
            function_name = ""
            try:
                # consume the first delta
                for event in completion:
                    delta = event["choices"][0]["delta"]
                    # Check if a function is called
                    if not delta.get("function_call"):
                        self.functionJustCalled = True
                    elif "name" in delta["function_call"]:
                        function_name = delta["function_call"]["name"]
                    # check the first delta is enough
                    break
                # Continue only when a function is called
                if self.functionJustCalled:
                    break

                # get stream function response message
                response_message = self.getStreamFunctionResponseMessage(completion, function_name)

                # get function response
                function_response = self.getFunctionResponse(response_message, function_name)

                # process function response
                # send the info on the function call and function response to GPT
                thisMessage.append(response_message) # extend conversation with assistant's reply
                thisMessage.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response

                self.functionJustCalled = True

                if not config.chatAfterFunctionCalled:
                    progress_callback.emit("\n\n~~~ ")
                    progress_callback.emit(function_response)
                    return None
            except:
                self.showErrors()
                break

        return completion

    def showErrors(self):
        if config.developer:
            print(traceback.format_exc())

    def getResponse(self, messages, progress_callback, functionJustCalled=False):
        responses = ""
        if config.chatApiLoadingInternetSearches == "always" and not functionJustCalled:
            #print("loading internet searches ...")
            try:
                completion = openai.ChatCompletion.create(
                    model=config.chatGPTApiModel,
                    messages=messages,
                    max_tokens=config.chatGPTApiMaxTokens,
                    temperature=config.chatGPTApiTemperature,
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
                        progress = event if isinstance(event, str) else event.choices[0].delta.content
                        # STREAM THE ANSWER
                        progress_callback.emit(progress)
            else:
                if config.chatGPTApiFunctionSignatures:
                    completion = openai.ChatCompletion.create(
                        model=config.chatGPTApiModel,
                        messages=messages,
                        max_tokens=config.chatGPTApiMaxTokens,
                        temperature=0.0 if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatGPTApiTemperature,
                        n=config.chatApiNoOfChoices,
                        functions=config.chatGPTApiFunctionSignatures,
                        function_call={"name": "run_python"} if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatApiFunctionCall,
                    )
                else:
                    completion = openai.ChatCompletion.create(
                        model=config.chatGPTApiModel,
                        messages=messages,
                        max_tokens=config.chatGPTApiMaxTokens,
                        temperature=config.chatGPTApiTemperature,
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
        # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            responses = f"OpenAI API returned an API Error: {e}"
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            responses = f"Failed to connect to OpenAI API: {e}"
        except openai.error.RateLimitError as e:
            #Handle rate limit error (we recommend using exponential backoff)
            responses = f"OpenAI API request exceeded rate limit: {e}"
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