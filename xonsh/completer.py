from xonsh.completers.tools import *

# UniqueBible App command keywords

bibleKeywords = ["text", "studytext", "_chapters", "_bibleinfo", "_vnsc", "_vndc", "readchapter", "readverse", "readword", "readlexeme", "compare", "comparechapter", "count", "search", "andsearch", "orsearch", "advancedsearch", "regexsearch", "bible", "chapter", "main", "study", "read", "readsync", "_verses", "_biblenote"]
lexiconKeywords = ["lexicon", "searchlexicon", "reverselexicon"]
commentaryKeywords = ["_commentarychapters", "_commentaryinfo", "commentary", "_commentaryverses", "_commentary"]
referenceKeywords = ["_book", "book", "searchbook", "searself.crossPlatformchbookchapter"]
thirdPartyDictKeywords = ["thirddictionary", "searchthirddictionary", "s3dict", "3dict"]

# Get UniqueBible App local resources

from uniquebible import config as ubaconfig
from uniquebible.util.ConfigUtil import ConfigUtil
ConfigUtil.setup()
ubaconfig.noQt=True
from uniquebible.util.CrossPlatform import CrossPlatform
crossPlatform = CrossPlatform()
crossPlatform.setupResourceLists()
resources = crossPlatform.resources

@non_exclusive_completer
@contextual_completer
def ub_completer(context):
    if context.command and context.command.args and context.command.args[0].value == "ub" and context.command.prefix:
        check = " ".join([i.value for i in context.command.args[1:] if hasattr(i, "value")]) + context.command.prefix
        if re.search(f"^({'|'.join(bibleKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("bibleListAbb", [])])
        elif re.search("^concordance:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("strongBibleListAbb", [])])
        elif re.search(f"^({'|'.join(lexiconKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("lexiconList", [])])
        elif re.search("^data:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("dataList", [])])
        elif re.search(f"^({'|'.join(commentaryKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("commentaryListAbb", [])])
        elif re.search("^dictionary:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("dictionaryListAbb", [])])
        elif re.search("^encyclopedia:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("encyclopediaListAbb", [])])
        elif re.search(f"^({'|'.join(referenceKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("referenceBookList", [])])
        elif re.search(f"^({'|'.join(thirdPartyDictKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("thirdPartyDictionaryList", [])])
        elif re.search("^searchtool:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in resources.get("searchToolList", [])])
completer add "ub_completer" ub_completer "start"

# Get UniqueBible App API resources
import requests, re
private = f"private={ubaconfig.web_api_private}&" if ubaconfig.web_api_private else ""
url = f"""{ubaconfig.web_api_endpoint}?{private}cmd=.resources"""
response = requests.get(url)
response.encoding = "utf-8"
api_resources = response.json()

@non_exclusive_completer
@contextual_completer
def ubapi_completer(context):
    if context.command and context.command.args and context.command.args[0].value in ('ubapi', 'uba') and context.command.prefix:
        check = " ".join([i.value for i in context.command.args[1:] if hasattr(i, "value")]) + context.command.prefix
        if re.search(f"^({'|'.join(bibleKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("bibleListAbb", [])])
        elif re.search("^concordance:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("strongBibleListAbb", [])])
        elif re.search(f"^({'|'.join(lexiconKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("lexiconList", [])])
        elif re.search("^data:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("dataList", [])])
        elif re.search(f"^({'|'.join(commentaryKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("commentaryListAbb", [])])
        elif re.search("^dictionary:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("dictionaryListAbb", [])])
        elif re.search("^encyclopedia:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("encyclopediaListAbb", [])])
        elif re.search(f"^({'|'.join(referenceKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("referenceBookList", [])])
        elif re.search(f"^({'|'.join(thirdPartyDictKeywords)}):::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("thirdPartyDictionaryList", [])])
        elif re.search("^searchtool:::", check, re.IGNORECASE):
            return set([context.command.prefix+i for i in api_resources.get("searchToolList", [])])
completer add "ubapi_completer" ubapi_completer "start"
