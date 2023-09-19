import config, json


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
    # retrieve argument values from a dictionary
    #print(function_args)
    function_args = function_args.get("code") # required

    insert_string = "import config\nconfig.pythonFunctionResponse = "
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
