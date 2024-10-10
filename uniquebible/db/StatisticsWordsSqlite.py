import os, apsw
import re

from uniquebible import config
from uniquebible.util.BibleBooks import BibleBooks


class StatisticsWordsSqlite:

    FILE_DIRECTORY = "statistics"
    FILE_NAME = "words.stats"
    COLOR_MAPPING_FILE = "frequency_color_mapping"
    TABLE_NAME = "data"
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {0} (Strongs NVARCHAR(6), Original NVARCHAR(50), Transliteration NVARCHAR(50), Frequency INT)".format(TABLE_NAME)

    def __init__(self):
        indexDir = os.path.join(config.marvelData, self.FILE_DIRECTORY)
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        self.filename = os.path.join(config.marvelData, self.FILE_DIRECTORY, self.FILE_NAME)
        if os.path.exists(indexDir):
            self.connection = apsw.Connection(self.filename)
            self.cursor = self.connection.cursor()
            # if not self.checkTableExists():
            #     self.createTable()

    def close(self):
        self.connection.close()

    def createTable(self):
        self.cursor.execute(self.CREATE_TABLE)

    def checkTableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(self.TABLE_NAME))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def insert(self, strongs, original, transliteration, frequency):
        if not self.checkStrongsExists(strongs):
            insert = "INSERT INTO {0} (Strongs, Original, Transliteration, Frequency) VALUES (?, ?, ?, ?)".format(self.TABLE_NAME)
            self.cursor.execute(insert, (strongs, original, transliteration, frequency))

    def delete(self, strongs):
        delete = "DELETE FROM {0} WHERE Strongs=?".format(self.TABLE_NAME)
        self.cursor.execute(delete, (strongs,))

    def deleteAll(self):
        delete = "DELETE FROM {0}".format(self.TABLE_NAME)
        self.cursor.execute(delete)

    def deleteHebrew(self):
        delete = "DELETE FROM {0} WHERE Strongs like 'H%'".format(self.TABLE_NAME)
        self.cursor.execute(delete)

    def deleteGreek(self):
        delete = "DELETE FROM {0} WHERE Strongs like 'G%'".format(self.TABLE_NAME)
        self.cursor.execute(delete)

    def checkStrongsExists(self, Strongs):
        query = "SELECT * FROM {0} WHERE Strongs=?".format(self.TABLE_NAME)
        self.cursor.execute(query, (Strongs,))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def getFrequency(self, strongs):
        query = "SELECT Frequency FROM {0} WHERE Strongs=?".format(self.TABLE_NAME)
        self.cursor.execute(query, (strongs,))
        data = self.cursor.fetchone()
        if data:
            return int(str(data[0]).replace(",", ""))
        else:
            return 0

    def getAllStrongsFrequency(self):
        query = "SELECT Strongs, Frequency FROM {0} ORDER BY Strongs".format(self.TABLE_NAME)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getAll(self):
        query = "SELECT * FROM {0} ORDER BY Strongs".format(self.TABLE_NAME)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def testCreate(self):
        self.deleteAll()
        self.insert("G2424", "Ἰησοῦς", "Iēsous", "975")

    def listAll(self):
        records = self.getAll()
        for record in records:
            print("{0}:{1}:{2}:{3}".format(record[0], record[1], record[2], record[3]))

    # Almost 15,000 unique Strongs words
    # 5,624 Greek - Actual 5502
    # 8,674 Hebrew - Actual 8513
    # https://en.wikipedia.org/wiki/Strong%27s_Concordance
    def populateDatabase(self, language="H", delete=False, strongsToImport=[]):

        from uniquebible.db.ToolsSqlite import Lexicon

        if delete:
            if language == "H":
                self.deleteHebrew()
            else:
                self.deleteGreek()

        lexicon = Lexicon('TRLIT')
        if len(strongsToImport) > 0:
            topics = strongsToImport
        elif language == "H":
            topics = lexicon.getHebrewTopics()
        else:
            topics = lexicon.getGreekTopics()
        print("Processing " + str(len(topics)))
        max_records = 15000
        count = 0
        for data in topics:
            strongs = data[0]
            data = lexicon.getRawContent(strongs)
            if data:
                entry = data[0]
            if data and entry and "Transliteration" in entry and "Occurs" in entry:
                entry = entry.replace("\n", " ")
                if count % 1000 == 0:
                    print(count)
                try:
                    search = re.search(r"<grk>(.*?)</grk>.*Transliteration: .*?>(.*?)<\/a>.*?Occurs (.*?) ", entry)
                    (original, transliteration, frequency) = search.groups()
                    # print("{0}:{1}".format(transliteration, frequency))
                except:
                    print("Error in " + strongs)
                if not self.checkStrongsExists(strongs):
                    self.insert(strongs, original.strip(), transliteration, frequency)

            count += 1
            if count > max_records:
                break

    def addHighlightTagToPreviousWord(self, text, searchWord, color, frequency):
        searchWord = " " + searchWord + " "
        startSearch = 0
        while searchWord in text[startSearch:]:
            end_ptr = text.find(searchWord, startSearch)
            start_ptr = end_ptr - 1
            while text[start_ptr] not in (' ', '>'):
                start_ptr = start_ptr - 1
                if start_ptr == 0:
                    break
            if start_ptr > 0:
                start_ptr =start_ptr + 1
            replaceWord = text[start_ptr:end_ptr].strip()
            matches = re.search(r"[GH][0-9]*?", replaceWord)
            if matches:
                replace = replaceWord
            else:
                replace = '<span style="color: ' + color + '">' + replaceWord + ' <sub>' + str(frequency) + '</sub></span>'
                text = text[:start_ptr] + replace + text[end_ptr:]
            startSearch = end_ptr + len(replace)
        return text

    def loadHighlightMappingFile(self, customFile = "custom"):
        filename = self.COLOR_MAPPING_FILE + "_" + customFile + ".txt"
        mappingFilename = os.path.join(config.marvelData, self.FILE_DIRECTORY, filename)
        if not os.path.exists(mappingFilename):
            filename = self.COLOR_MAPPING_FILE + ".txt"
            mappingFilename = os.path.join(config.marvelData, self.FILE_DIRECTORY, filename)

        highlightMapping = []
        with open(mappingFilename) as f:
            for line in f:
                line = line.strip()
                if len(line) == 0 or line[0] == "#":
                    pass
                else:
                    data = [elt.strip() for elt in line.split(',')]
                    highlightMapping.append(data)
        return highlightMapping

    def findMissingLexicons(self, start, end):
        from uniquebible.db.BiblesSqlite import BiblesSqlite

        biblesSqlite = BiblesSqlite()
        missingStrongs = set()

        for book in range(start, end):
            print(book)
            chapters = BibleBooks.chapters[book]
            for chapter in range(1, chapters):
                contents = biblesSqlite.readTextChapter("KJVx", book, chapter)
                for line in contents:
                    text = line[3]
                    matches = re.findall(r" ([GH][0-9]*?) ", text)
                    for strongs in set(matches):
                        frequency = self.getFrequency(strongs)
                        if frequency == 0:
                            missingStrongs.add(strongs)
        for strongs in missingStrongs:
            print("./cs.sh " + strongs)
        data = []
        for strongs in missingStrongs:
            data.append((strongs, ''))
        print(str(data))

    def testReplace(self):
        # text = "The book G976 of the generation G2193 G1078 of Jesus G2424 Christ G5547 , the son G5207 of David G1138 , the son G5207 of Abraham G11 ."
        text = "generation G1078 G2193 Abraham G2193 G11 ."

        matches = re.findall(r" ([GH][0-9]*?) ", text)

        highlightMapping = self.loadHighlightMappingFile()

        for strongs in set(matches):
            frequency = self.getFrequency(strongs)
            color = ""
            for map in highlightMapping:
                if frequency >= int(map[0]) and frequency <= int(map[1]):
                    if config.theme in ("dark", "night"):
                        color = map[3]
                    else:
                        color = map[2]
            if color:
                text = self.addHighlightTagToPreviousWord(text, strongs, color, frequency)
        print(text)


if __name__ == "__main__":

    config.noQt = True
    config.mainB = ''
    config.mainC = ''
    config.mainV = ''
    config.mainText = ''
    config.commentaryB = ''
    config.commentaryC = ''
    config.commentaryV = ''
    config.commentaryText = ''
    config.theme = 'dark'

    config.marvelData = "/home/oliver/dev/UniqueBible/marvelData/"

    db = StatisticsWordsSqlite()

    # db.testCreate()
    # db.listAll()

    # db.testReplace()

    # db.loadHighlightMappingFile()

    # db.populateDatabase('G', True)

    db.findMissingLexicons(40, 67)

    # Run elh.sh

    # strongs = [('H7724', ''), ('H3385', ''), ('H4006', ''), ('H474', ''), ('H1044', ''), ('H6878', ''), ('H2305', ''), ('H467', ''), ('H3142', ''), ('H532', ''), ('H4965', ''), ('H3354', ''), ('H7525', ''), ('H8174', ''), ('H8039', ''), ('H1953', ''), ('H1989', ''), ('H8466', ''), ('H1199', ''), ('H2619', ''), ('H2044', ''), ('H5610', ''), ('H6905', ''), ('H3094', ''), ('H4777', ''), ('H466', ''), ('H3246', ''), ('H1928', ''), ('H832', ''), ('H3360', ''), ('H5620', ''), ('H7498', ''), ('H3421', ''), ('H1839', ''), ('H1230', ''), ('H1873', ''), ('H326', ''), ('H3403', ''), ('H1118', ''), ('H3300', ''), ('H2369', ''), ('H1074', ''), ('H5734', ''), ('H756', ''), ('H5163', ''), ('H8500', ''), ('H4338', ''), ('H5660', ''), ('H706', ''), ('H4052', ''), ('H6000', ''), ('H7821', ''), ('H2807', ''), ('H1914', ''), ('H8070', ''), ('H5471', ''), ('H7265', ''), ('H1489', ''), ('H4528', ''), ('H869', ''), ('H5370', ''), ('H3454', ''), ('H1256', ''), ('H2033', ''), ('H3434', ''), ('H5752', ''), ('H3088', ''), ('H5990', ''), ('H5593', ''), ('H7763', ''), ('H7470', ''), ('H2198', ''), ('H4019', ''), ('H2997', ''), ('H6573', ''), ('H4193', ''), ('H2160', ''), ('H863', ''), ('H7734', ''), ('H1139', ''), ('H45', ''), ('H4527', ''), ('H5419', ''), ('H5985', ''), ('H8206', ''), ('H1987', ''), ('H7987', ''), ('H8260', ''), ('H2979', ''), ('H7066', ''), ('H4416', ''), ('H8049', ''), ('H4238', ''), ('H1312', ''), ('H1303', ''), ('H396', ''), ('H274', ''), ('H3483', ''), ('H1493', ''), ('H2644', ''), ('H5717', ''), ('H6392', ''), ('H4447', ''), ('H848', ''), ('H6271', ''), ('H7149', ''), ('H7894', ''), ('H5814', ''), ('H38', ''), ('H43', ''), ('H2987', ''), ('H3534', ''), ('H3431', ''), ('H3736', ''), ('H3457', ''), ('H382', ''), ('H1983', ''), ('H8468', ''), ('H2080', ''), ('H1325', ''), ('H8315', ''), ('H8188', ''), ('H1597', ''), ('H3203', ''), ('H1176', ''), ('H2591', ''), ('H1776', ''), ('H4495', ''), ('H1132', ''), ('H4925', ''), ('H6732', ''), ('H4837', ''), ('H2124', ''), ('H1340', ''), ('H1798', ''), ('H5477', ''), ('H3262', ''), ('H3449', ''), ('H8137', ''), ('H8507', ''), ('H6909', ''), ('H8402', ''), ('H2880', ''), ('H8430', ''), ('H2477', ''), ('H1579', ''), ('H1294', ''), ('H3879', ''), ('H8037', ''), ('H7016', ''), ('H257', ''), ('H3192', ''), ('H4505', ''), ('H2798', ''), ('H261', ''), ('H2792', ''), ('H770', ''), ('H8434', ''), ('H5114', ''), ('H2537', ''), ('H6432', ''), ('H6768', ''), ('H6494', ''), ('H2364', ''), ('H6450', ''), ('H3592', ''), ('H3674', ''), ('H6506', ''), ('H484', ''), ('H6122', ''), ('H3359', ''), ('H8390', ''), ('H6661', ''), ('H3170', ''), ('H8536', ''), ('H8520', ''), ('H6262', ''), ('H806', ''), ('H450', ''), ('H3620', ''), ('H710', ''), ('H3151', ''), ('H2359', ''), ('H1282', ''), ('H3472', ''), ('H8124', ''), ('H6462', ''), ('H5683', ''), ('H5928', ''), ('H3140', ''), ('H5119', ''), ('H2641', ''), ('H6065', ''), ('H7952', ''), ('H7787', ''), ('H112', ''), ('H7437', ''), ('H3181', ''), ('H8054', ''), ('H496', ''), ('H1585', ''), ('H7532', ''), ('H222', ''), ('H5261', ''), ('H266', ''), ('H3450', ''), ('H5252', ''), ('H3072', ''), ('H2241', ''), ('H2144', ''), ('H2503', ''), ('H3388', ''), ('H493', ''), ('H2886', ''), ('H701', ''), ('H414', ''), ('H1862', ''), ('H8230', ''), ('H6457', ''), ('H2566', ''), ('H4807', ''), ('H3080', ''), ('H3031', ''), ('H1950', ''), ('H1685', ''), ('H4587', ''), ('H3234', ''), ('H2069', ''), ('H5675', ''), ('H4061', ''), ('H3635', ''), ('H153', ''), ('H896', ''), ('H3014', ''), ('H1807', ''), ('H22', ''), ('H4921', ''), ('H1480', ''), ('H407', ''), ('H6717', ''), ('H8349', ''), ('H4382', ''), ('H7767', ''), ('H1003', ''), ('H1723', ''), ('H351', ''), ('H5811', ''), ('H4907', ''), ('H1150', ''), ('H7792', ''), ('H7316', ''), ('H7346', ''), ('H2323', ''), ('H6868', ''), ('H5171', ''), ('H7855', ''), ('H849', ''), ('H3239', ''), ('H252', ''), ('H8013', ''), ('H2819', ''), ('H5295', ''), ('H477', ''), ('H2839', ''), ('H8123', ''), ('H1424', ''), ('H2743', ''), ('H4287', ''), ('H4653', ''), ('H6554', ''), ('H1784', ''), ('H2536', ''), ('H3398', ''), ('H1495', ''), ('H5293', ''), ('H7798', ''), ('H2171', ''), ('H3439', ''), ('H4274', ''), ('H6871', ''), ('H1184', ''), ('H867', ''), ('H3040', ''), ('H2211', ''), ('H5256', ''), ('H2829', ''), ('H5721', ''), ('H7320', ''), ('H2120', ''), ('H8187', ''), ('H1075', ''), ('H3404', ''), ('H2745', ''), ('H7888', ''), ('H2882', ''), ('H1276', ''), ('H7513', ''), ('H5069', ''), ('H3319', ''), ('H7780', ''), ('H8113', ''), ('H2127', ''), ('H3914', ''), ('H1147', ''), ('H5565', ''), ('H1451', ''), ('H8022', ''), ('H3229', ''), ('H115', ''), ('H8332', ''), ('H4413', ''), ('H6048', ''), ('H443', ''), ('H3578', ''), ('H8101', ''), ('H2066', ''), ('H50', ''), ('H3333', ''), ('H3902', ''), ('H3131', ''), ('H2460', ''), ('H3291', ''), ('H3174', ''), ('H2381', ''), ('H5412', ''), ('H4235', ''), ('H2117', ''), ('H1135', ''), ('H3090', ''), ('H3855', ''), ('H3356', ''), ('H771', ''), ('H1188', ''), ('H6273', ''), ('H3035', ''), ('H3549', ''), ('H8094', ''), ('H8616', ''), ('H5073', ''), ('H4252', ''), ('H1596', ''), ('H5866', ''), ('H7501', ''), ('H620', ''), ('H5873', ''), ('H6142', ''), ('H964', ''), ('H1531', ''), ('H6574', ''), ('H5316', ''), ('H3501', ''), ('H1169', ''), ('H1273', ''), ('H8100', ''), ('H670', ''), ('H7441', ''), ('H5626', ''), ('H2468', ''), ('H5583', ''), ('H3043', ''), ('H1332', ''), ('H2321', ''), ('H8060', ''), ('H1017', ''), ('H4212', ''), ('H1190', ''), ('H1485', ''), ('H7598', ''), ('H5538', ''), ('H2840', ''), ('H5052', ''), ('H5962', ''), ('H7619', ''), ('H7572', ''), ('H5815', ''), ('H179', ''), ('H7345', ''), ('H31', ''), ('H8200', ''), ('H1735', ''), ('H3316', ''), ('H1134', ''), ('H5722', ''), ('H1956', ''), ('H3139', ''), ('H850', ''), ('H7861', ''), ('H4444', ''), ('H1202', ''), ('H2361', ''), ('H5865', ''), ('H144', ''), ('H2311', ''), ('H4582', ''), ('H2217', ''), ('H2755', ''), ('H5495', ''), ('H2126', ''), ('H8091', ''), ('H5196', ''), ('H2669', ''), ('H3185', ''), ('H3269', ''), ('H8395', ''), ('H5232', ''), ('H3230', ''), ('H3679', ''), ('H5925', ''), ('H4255', ''), ('H7380', ''), ('H89', ''), ('H7746', ''), ('H3172', ''), ('H2680', ''), ('H7841', ''), ('H1048', ''), ('H3160', ''), ('H4344', ''), ('H6469', ''), ('H4323', ''), ('H1938', ''), ('H21', ''), ('H6397', ''), ('H745', ''), ('H6007', ''), ('H2996', ''), ('H671', ''), ('H2458', ''), ('H8030', ''), ('H8488', ''), ('H6861', ''), ('H5072', ''), ('H4237', ''), ('H7204', ''), ('H3166', ''), ('H3141', ''), ('H807', ''), ('H5904', ''), ('H3507', ''), ('H4789', ''), ('H4510', ''), ('H2695', ''), ('H547', ''), ('H291', ''), ('H6173', ''), ('H4012', ''), ('H1275', ''), ('H104', ''), ('H5446', ''), ('H5836', ''), ('H452', ''), ('H2125', ''), ('H3408', ''), ('H593', ''), ('H463', ''), ('H2155', ''), ('H2072', ''), ('H6795', ''), ('H4319', ''), ('H2510', ''), ('H447', ''), ('H4357', ''), ('H5225', ''), ('H5896', ''), ('H4626', ''), ('H4648', ''), ('H8118', ''), ('H3210', ''), ('H7889', ''), ('H1033', ''), ('H7276', ''), ('H7051', ''), ('H1178', ''), ('H3137', ''), ('H6036', ''), ('H4331', ''), ('H8652', ''), ('H2690', ''), ('H3041', ''), ('H3479', ''), ('H3092', ''), ('H229', ''), ('H6254', ''), ('H3099', ''), ('H302', ''), ('H8329', ''), ('H3604', ''), ('H3296', ''), ('H3057', ''), ('H3575', ''), ('H2024', ''), ('H3260', ''), ('H1051', ''), ('H8654', ''), ('H3964', ''), ('H6336', ''), ('H8287', ''), ('H5900', ''), ('H6232', ''), ('H169', ''), ('H8472', ''), ('H1057', ''), ('H150', ''), ('H2774', ''), ('H3146', ''), ('H4656', ''), ('H8043', ''), ('H1338', ''), ('H6560', ''), ('H619', ''), ('H7480', ''), ('H135', ''), ('H6134', ''), ('H8225', ''), ('H1490', ''), ('H3889', ''), ('H4056', ''), ('H508', ''), ('H4734', ''), ('H3263', ''), ('H8674', ''), ('H2802', ''), ('H7029', ''), ('H5598', ''), ('H8407', ''), ('H7634', ''), ('H6054', ''), ('H6402', ''), ('H3805', ''), ('H6889', ''), ('H3197', ''), ('H8119', ''), ('H58', ''), ('H878', ''), ('H3562', ''), ('H7871', ''), ('H3613', ''), ('H918', ''), ('H4028', ''), ('H4920', ''), ('H163', ''), ('H6200', ''), ('H8290', ''), ('H7868', ''), ('H497', ''), ('H4049', ''), ('H6841', ''), ('H3253', ''), ('H275', ''), ('H8412', ''), ('H7395', ''), ('H5525', ''), ('H315', ''), ('H3495', ''), ('H1726', ''), ('H141', ''), ('H2432', ''), ('H3152', ''), ('H1232', ''), ('H4558', ''), ('H3769', ''), ('H3469', ''), ('H7940', ''), ('H279', ''), ('H8448', ''), ('H6644', ''), ('H3301', ''), ('H3164', ''), ('H4873', ''), ('H3258', ''), ('H4987', ''), ('H36', ''), ('H412', ''), ('H1013', ''), ('H6997', ''), ('H829', ''), ('H4208', ''), ('H715', ''), ('H8348', ''), ('H8114', ''), ('H6520', ''), ('H3746', ''), ('H7719', ''), ('H4737', ''), ('H5901', ''), ('H3144', ''), ('H2899', ''), ('H654', ''), ('H5812', ''), ('H1437', ''), ('H3297', ''), ('H649', ''), ('H3056', ''), ('H5017', ''), ('H3108', ''), ('H6971', ''), ('H7977', ''), ('H3706', ''), ('H5013', ''), ('H5654', ''), ('H4162', ''), ('H2702', ''), ('H7869', ''), ('H1183', ''), ('H2402', ''), ('H3380', ''), ('H4458', ''), ('H2105', ''), ('H3433', ''), ('H978', ''), ('H242', ''), ('H8370', ''), ('H300', ''), ('H66', ''), ('H880', ''), ('H6022', ''), ('H1577', ''), ('H3194', ''), ('H2249', ''), ('H5180', ''), ('H2301', ''), ('H4776', ''), ('H3047', ''), ('H478', ''), ('H4381', ''), ('H6637', ''), ('H791', ''), ('H1946', ''), ('H3073', ''), ('H6474', ''), ('H3329', ''), ('H3922', ''), ('H1309', ''), ('H5026', ''), ('H5724', ''), ('H8325', ''), ('H4954', ''), ('H418', ''), ('H3155', ''), ('H7288', ''), ('H129', ''), ('H4491', ''), ('H105', ''), ('H4640', ''), ('H5224', ''), ('H3810', ''), ('H1182', ''), ('H6886', ''), ('H2338', ''), ('H1560', ''), ('H1001', ''), ('H5744', ''), ('H3086', ''), ('H6515', ''), ('H51', ''), ('H3285', ''), ('H6981', ''), ('H3496', ''), ('H4322', ''), ('H149', ''), ('H2867', ''), ('H3265', ''), ('H5964', ''), ('H4619', ''), ('H7652', ''), ('H6391', ''), ('H1737', ''), ('H6746', ''), ('H7506', ''), ('H5084', ''), ('H1402', ''), ('H792', ''), ('H4004', ''), ('H8662', ''), ('H989', ''), ('H3621', ''), ('H8634', ''), ('H6080', ''), ('H2037', ''), ('H2998', ''), ('H1940', ''), ('H4667', ''), ('H2378', ''), ('H7421', ''), ('H5827', ''), ('H2466', ''), ('H1483', ''), ('H5334', ''), ('H6645', ''), ('H4877', ''), ('H2228', ''), ('H3935', ''), ('H3298', ''), ('H307', ''), ('H3703', ''), ('H5604', ''), ('H2129', ''), ('H3078', ''), ('H4697', ''), ('H6568', ''), ('H5406', ''), ('H3143', ''), ('H7109', ''), ('H4821', ''), ('H920', ''), ('H2955', ''), ('H8028', ''), ('H6084', ''), ('H5540', ''), ('H267', ''), ('H3236', ''), ('H7842', ''), ('H6377', ''), ('H2322', ''), ('H3560', ''), ('H629', ''), ('H6222', ''), ('H5917', ''), ('H3668', ''), ('H8125', ''), ('H4346', ''), ('H5851', ''), ('H1307', ''), ('H5613', ''), ('H1093', ''), ('H4887', ''), ('H3191', ''), ('H7877', ''), ('H4040', ''), ('H846', ''), ('H37', ''), ('H287', ''), ('H2071', ''), ('H6164', ''), ('H4140', ''), ('H462', ''), ('H5893', ''), ('H5185', ''), ('H4067', ''), ('H3402', ''), ('H2478', ''), ('H7154', ''), ('H8126', ''), ('H5277', ''), ('H8007', ''), ('H3461', ''), ('H4677', ''), ('H6882', ''), ('H3273', ''), ('H6769', ''), ('H2360', ''), ('H5991', ''), ('H8116', ''), ('H4233', ''), ('H4779', ''), ('H8115', ''), ('H3145', ''), ('H5854', ''), ('H3268', ''), ('H1563', ''), ('H1255', ''), ('H2780', ''), ('H2424', ''), ('H5834', ''), ('H3949', ''), ('H690', ''), ('H5313', ''), ('H1492', ''), ('H5993', ''), ('H674', ''), ('H683', ''), ('H7566', ''), ('H1279', ''), ('H4981', ''), ('H2285', ''), ('H3890', ''), ('H3740', ''), ('H7669', ''), ('H3675', ''), ('H6874', ''), ('H3397', ''), ('H5859', ''), ('H2237', ''), ('H8491', ''), ('H3089', ''), ('H5796', ''), ('H8436', ''), ('H1810', ''), ('H2365', ''), ('H388', ''), ('H8664', ''), ('H1395', ''), ('H7472', ''), ('H2984', ''), ('H5407', ''), ('H5029', ''), ('H8589', ''), ('H3942', ''), ('H7801', ''), ('H3005', ''), ('H2515', ''), ('H1240', ''), ('H767', ''), ('H3430', ''), ('H841', ''), ('H5616', ''), ('H2281', ''), ('H3339', ''), ('H5831', ''), ('H4990', ''), ('H3109', ''), ('H563', ''), ('H7005', ''), ('H6652', ''), ('H3132', ''), ('H5386', ''), ('H8340', ''), ('H1388', ''), ('H4778', ''), ('H3386', ''), ('H682', ''), ('H6046', ''), ('H4337', ''), ('H6221', ''), ('H6984', ''), ('H8527', ''), ('H1936', ''), ('H873', ''), ('H2757', ''), ('H3189', ''), ('H3075', ''), ('H8223', ''), ('H3473', ''), ('H7303', ''), ('H6483', ''), ('H465', ''), ('H2293', ''), ('H1452', ''), ('H4329', ''), ('H4638', ''), ('H8261', ''), ('H7681', ''), ('H3758', ''), ('H8253', ''), ('H3464', ''), ('H2043', ''), ('H7625', ''), ('H704', ''), ('H2733', ''), ('H840', ''), ('H6745', ''), ('H4856', ''), ('H5325', ''), ('H673', ''), ('H3663', ''), ('H610', ''), ('H7996', ''), ('H2453', ''), ('H4097', ''), ('H924', ''), ('H3883', ''), ('H7671', ''), ('H3171', ''), ('H7609', ''), ('H6070', ''), ('H5915', ''), ('H348', ''), ('H3292', ''), ('H3573', ''), ('H304', ''), ('H8405', ''), ('H277', ''), ('H198', ''), ('H3406', ''), ('H5757', ''), ('H1529', ''), ('H4636', ''), ('H8053', ''), ('H2093', ''), ('H4849', ''), ('H379', ''), ('H726', ''), ('H7978', ''), ('H5793', ''), ('H1398', ''), ('H1522', ''), ('H3275', ''), ('H2059', ''), ('H4727', ''), ('H8647', ''), ('H1592', ''), ('H8493', ''), ('H6220', ''), ('H265', ''), ('H3149', ''), ('H498', ''), ('H2967', ''), ('H749', ''), ('H787', ''), ('H4415', ''), ('H1359', ''), ('H6503', ''), ('H5681', ''), ('H5581', ''), ('H2841', ''), ('H3059', ''), ('H2395', ''), ('H3466', ''), ('H3480', ''), ('H4251', ''), ('H8461', ''), ('H8073', ''), ('H2133', ''), ('H2741', ''), ('H220', ''), ('H4343', ''), ('H7435', ''), ('H5179', ''), ('H448', ''), ('H5444', ''), ('H5661', ''), ('H313', ''), ('H1939', ''), ('H1791', ''), ('H6894', ''), ('H5885', ''), ('H4552', ''), ('H5294', ''), ('H1453', ''), ('H1636', ''), ('H2578', ''), ('H1799', ''), ('H6498', ''), ('H4913', ''), ('H3400', ''), ('H6737', ''), ('H316', ''), ('H4535', ''), ('H3660', ''), ('H5524', ''), ('H49', ''), ('H2679', ''), ('H3135', ''), ('H3375', ''), ('H3475', ''), ('H7756', ''), ('H1837', ''), ('H3834', ''), ('H1686', ''), ('H62', ''), ('H5806', ''), ('H6858', ''), ('H3443', ''), ('H3134', ''), ('H4922', ''), ('H7774', ''), ('H6516', ''), ('H6407', ''), ('H723', ''), ('H4443', ''), ('H3165', ''), ('H3060', ''), ('H8339', ''), ('H6690', ''), ('H1122', ''), ('H3163', ''), ('H7558', ''), ('H7352', ''), ('H4243', ''), ('H6753', ''), ('H1218', ''), ('H1684', ''), ('H8475', ''), ('H4936', ''), ('H2647', ''), ('H4078', ''), ('H1702', ''), ('H3428', ''), ('H6811', ''), ('H2718', ''), ('H7357', ''), ('H71', ''), ('H4732', ''), ('H6404', ''), ('H3936', ''), ('H2456', ''), ('H946', ''), ('H2621', ''), ('H3310', ''), ('H4226', ''), ('H684', ''), ('H6570', ''), ('H8638', ''), ('H1269', ''), ('H284', ''), ('H1171', ''), ('H3294', ''), ('H3085', ''), ('H4378', ''), ('H4810', ''), ('H3460', ''), ('H2383', ''), ('H1782', ''), ('H6859', ''), ('H6816', ''), ('H5738', ''), ('H1011', ''), ('H3436', ''), ('H5250', '')]
    # db.populateDatabase("H", False, strongs)

