from uniquebible import config
import json, re


# ChatGPT-GUI plugin: Instruct ChatGPT to excute python code directly in response to user input
# Written by: Eliran Wong
# Feature: Non-python users can use natural language to instruct ChatGPT to perform whatever tasks which python is capable to do.

# Usage:
# 1. Select "Execute Python Code" as predefined context
# 2. Use natural language to instruct ChatGPT to execute what python is capable to do
# 
# Examples, try:
# Tell me the current time.
# Tell me how many files in the current directory.
# What is my operating system and version?
# Is google chrome installed on this computer?
# Open web browser.
# Open https://github.com/eliranwong/ChatGPT-GUI in a web browser.
# Search ChatGPT in a web browser.
# Open the current directory using the default file manager.
# Open VLC player.

def run_python(function_args):
    def fineTunePythonCode(code):
        insert_string = "from uniquebible import config\nconfig.pythonFunctionResponse = "
        code = re.sub("^!(.*?)$", r"import os\nos.system(\1)", code, flags=re.M)
        if "\n" in code:
            substrings = code.rsplit("\n", 1)
            lastLine = re.sub("print\((.*)\)", r"\1", substrings[-1])
            code = code if lastLine.startswith(" ") else f"{substrings[0]}\n{insert_string}{lastLine}"
        else:
            code = f"{insert_string}{code}"
        return code

    # retrieve argument values from a dictionary
    #print(function_args)
    function_args = function_args.get("code") # required
    new_function_args = fineTunePythonCode(function_args)
    try:
        exec(new_function_args, globals())
        function_response = str(config.pythonFunctionResponse)
    except:
        function_response = function_args
    info = {"information": function_response}
    function_response = json.dumps(info)
    return json.dumps(info)

functionSignature = {
    "name": "run_python",
    "description": "Execute python code",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "python code, e.g. print('Hello world')",
            },
        },
        "required": ["code"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["run_python"] = run_python
config.predefinedContexts["Execute Python Code"] = """Execute python codes directly on my behalf to achieve the following tasks.  Do not show me the codes."""
