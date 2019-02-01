import os, sqlite3, config

class ThirdPartyDictionary:

    def __init__(self, module):
        self.module = module
        self.moduleList = self.getModuleList()
        if self.module in self.moduleList:
            self.database = os.path.join("thirdParty", "dictionaries", "{0}.dct.mybible".format(module))
            self.connection = sqlite3.connect(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getModuleList(self):
        moduleFolder = os.path.join("thirdParty", "dictionaries")
        return [f[:-12] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dct.mybible")]

    def search(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            exactMatch = self.getExactWord(entry)
            similarMatch = self.getSimilarWord(entry)
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            return "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2><p>{4}</p><p><b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}".format(self.module, entry, exactMatch, similarMatch, selectList)

    def formatSelectList(self, action, optionList):
        selectForm = "<select onchange='{0}'>".format(action)
        for value, description in optionList:
            if value == self.module:
                selectForm += "<option value='{0}' selected='selected'>{1}</option>".format(value, description)
            else:
                selectForm += "<option value='{0}'>{1}</option>".format(value, description)
        selectForm += "</select>"
        return selectForm

    def getExactWord(self, entry):
        query = "SELECT word FROM dictionary WHERE word = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getSimilarWord(self, entry):
        query = "SELECT word FROM dictionary WHERE word LIKE ? AND word != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getData(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            query = "SELECT data FROM dictionary WHERE word = ?"
            self.cursor.execute(query, (entry,))
            content = self.cursor.fetchone()
            if not content:
                return "[not found]"
            else:
                action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
                optionList = [(m, m) for m in self.moduleList]
                selectList = self.formatSelectList(action, optionList)
                config.thirdDictionary = self.module
                return "<p>{0}</p><p>{1}</p>".format(selectList, content[0])
