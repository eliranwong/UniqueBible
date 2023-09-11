import config, json, googlesearch

# Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

def get_internet_info(function_args):
    # retrieve argument values from a dictionary
    #print(function_args)
    keywords = function_args.get("keywords") # required

    news = {}
    for index, item in enumerate(googlesearch.search(keywords, advanced=True, num_results=config.chatGPTApiMaximumInternetSearchResults)):
        news[f"result {index}"] = {
            "title": item.title,
            "url": item.url,
            "description": item.description,
        }
    return json.dumps(news)

functionSignature = {
    "name": "get_internet_info",
    "description": "Search internet for keywords when ChatGPT does not have information",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "keywords for searches, e.g. ChatGPT",
            },
        },
        "required": ["keywords"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["get_internet_info"] = get_internet_info