function textName(name) {
    document.title = "_bibleinfo:::"+name;
}

function commentaryName(name) {
    document.title = "_commentaryinfo:::"+name;
}

function bookName(name) {
    var fullname = getFullBookName(name);
    document.title = "_info:::"+fullname;
}

function getFullBookName(abbreviation) {
    var fullBookNameObject = {
        bGen: "Genesis",
        bExod: "Exodus",
        bLev: "Leviticus",
        bNum: "Numbers",
        bDeut: "Deuteronomy",
        bJosh: "Joshua",
        bJudg: "Judges",
        bRuth: "Ruth",
        b1Sam: "1 Samuel",
        b2Sam: "2 Samuel",
        b1Kgs: "1 Kings",
        b2Kgs: "2 Kings",
        b1Chr: "1 Chronicles",
        b2Chr: "2 Chronicles",
        bEzra: "Ezra",
        bNeh: "Nehemiah",
        bEsth: "Esther",
        bJob: "Job",
        bPs: "Psalms",
        bProv: "Proverbs",
        bEccl: "Ecclesiastes",
        bSong: "Song of Songs",
        bIsa: "Isaiah",
        bJer: "Jeremiah",
        bLam: "Lamentations",
        bEzek: "Ezekiel",
        bDan: "Daniel",
        bHos: "Hosea",
        bJoel: "Joel",
        bAmos: "Amos",
        bObad: "Obadiah",
        bJonah: "Jonah",
        bMic: "Micah",
        bNah: "Nahum",
        bHab: "Habakkuk",
        bZeph: "Zephaniah",
        bHag: "Haggai",
        bZech: "Zechariah",
        bMal: "Malachi",
        bMatt: "Matthew",
        bMark: "Mark",
        bLuke: "Luke",
        bJohn: "John",
        bActs: "Acts",
        bRom: "Romans",
        b1Cor: "1 Corinthians",
        b2Cor: "2 Corinthians",
        bGal: "Galatians",
        bEph: "Ephesians",
        bPhil: "Philippians",
        bCol: "Colossians",
        b1Thess: "1 Thessalonians",
        b2Thess: "2 Thessalonians",
        b1Tim: "1 Timothy",
        b2Tim: "2 Timothy",
        bTitus: "Titus",
        bPhlm: "Philemon",
        bHeb: "Hebrews",
        bJas: "James",
        b1Pet: "1 Peter",
        b2Pet: "2 Peter",
        b1John: "1 John",
        b2John: "2 John",
        b3John: "3 John",
        bJude: "Jude",
        bRev: "Revelation",
        bBar: "Baruch",
        bAddDan: "Additions to Daniel",
        bPrAzar: "Prayer of Azariah",
        bBel: "Bel and the Dragon",
        bSgThree: "Song of the Three Young Men",
        bSus: "Susanna",
        b1Esd: "1 Esdras",
        b2Esd: "2 Esdras",
        bAddEsth: "Additions to Esther",
        bEpJer: "Epistle of Jeremiah",
        bJdt: "Judith",
        b1Macc: "1 Maccabees",
        b2Macc: "2 Maccabees",
        b3Macc: "3 Maccabees",
        b4Macc: "4 Maccabees",
        bPrMan: "Prayer of Manasseh",
        bPs151: "Psalm 151",
        bSir: "Sirach",
        bTob: "Tobit",
        bWis: "Wisdom of Solomon",
        bPssSol: "Psalms of Solomon",
        bOdes: "Odes",
        bEpLao: "Epistle to the Laodiceans"
    };
    return fullBookNameObject["b"+abbreviation];
}

function bcvToVerseRefence(b,c,v) {
    var abbSBL = {
        ub1: "Gen",
        ub2: "Exod",
        ub3: "Lev",
        ub4: "Num",
        ub5: "Deut",
        ub6: "Josh",
        ub7: "Judg",
        ub8: "Ruth",
        ub9: "1Sam",
        ub10: "2Sam",
        ub11: "1Kgs",
        ub12: "2Kgs",
        ub13: "1Chr",
        ub14: "2Chr",
        ub15: "Ezra",
        ub16: "Neh",
        ub17: "Esth",
        ub18: "Job",
        ub19: "Ps",
        ub20: "Prov",
        ub21: "Eccl",
        ub22: "Song",
        ub23: "Isa",
        ub24: "Jer",
        ub25: "Lam",
        ub26: "Ezek",
        ub27: "Dan",
        ub28: "Hos",
        ub29: "Joel",
        ub30: "Amos",
        ub31: "Obad",
        ub32: "Jonah",
        ub33: "Mic",
        ub34: "Nah",
        ub35: "Hab",
        ub36: "Zeph",
        ub37: "Hag",
        ub38: "Zech",
        ub39: "Mal",
        ub40: "Matt",
        ub41: "Mark",
        ub42: "Luke",
        ub43: "John",
        ub44: "Acts",
        ub45: "Rom",
        ub46: "1Cor",
        ub47: "2Cor",
        ub48: "Gal",
        ub49: "Eph",
        ub50: "Phil",
        ub51: "Col",
        ub52: "1Thess",
        ub53: "2Thess",
        ub54: "1Tim",
        ub55: "2Tim",
        ub56: "Titus",
        ub57: "Phlm",
        ub58: "Heb",
        ub59: "Jas",
        ub60: "1Pet",
        ub61: "2Pet",
        ub62: "1John",
        ub63: "2John",
        ub64: "3John",
        ub65: "Jude",
        ub66: "Rev",
        ub70: "Bar",
        ub71: "AddDan",
        ub72: "PrAzar",
        ub73: "Bel",
        ub75: "Sus",
        ub76: "1Esd",
        ub77: "2Esd",
        ub78: "AddEsth",
        ub79: "EpJer",
        ub80: "Jdt",
        ub81: "1Macc",
        ub82: "2Macc",
        ub83: "3Macc",
        ub84: "4Macc",
        ub85: "PrMan",
        ub86: "Ps151",
        ub87: "Sir",
        ub88: "Tob",
        ub89: "Wis",
        ub90: "PssSol",
        ub91: "Odes",
        ub92: "EpLao"
    };
    var abb = abbSBL["ub"+String(b)];
    return abb+" "+c+":"+v;
}

function mbbcvToVerseRefence(b,c,v) {
    var abbSBL = {
        mb10: "Gen",
        mb20: "Exod",
        mb30: "Lev",
        mb40: "Num",
        mb50: "Deut",
        mb60: "Josh",
        mb61: "Josh",
        mb70: "Judg",
        mb71: "Judg",
        mb80: "Ruth",
        mb90: "1Sam",
        mb100: "2Sam",
        mb110: "1Kgs",
        mb120: "2Kgs",
        mb130: "1Chr",
        mb140: "2Chr",
        mb150: "Ezra",
        mb160: "Neh",
        mb190: "Esth",
        mb220: "Job",
        mb230: "Ps",
        mb240: "Prov",
        mb250: "Eccl",
        mb260: "Song",
        mb290: "Isa",
        mb300: "Jer",
        mb310: "Lam",
        mb330: "Ezek",
        mb340: "Dan",
        mb350: "Hos",
        mb360: "Joel",
        mb370: "Amos",
        mb380: "Obad",
        mb390: "Jonah",
        mb400: "Mic",
        mb410: "Nah",
        mb420: "Hab",
        mb430: "Zeph",
        mb440: "Hag",
        mb450: "Zech",
        mb460: "Mal",
        mb470: "Matt",
        mb480: "Mark",
        mb490: "Luke",
        mb500: "John",
        mb510: "Acts",
        mb520: "Rom",
        mb530: "1Cor",
        mb540: "2Cor",
        mb550: "Gal",
        mb560: "Eph",
        mb570: "Phil",
        mb580: "Col",
        mb590: "1Thess",
        mb600: "2Thess",
        mb610: "1Tim",
        mb620: "2Tim",
        mb630: "Titus",
        mb640: "Phlm",
        mb650: "Heb",
        mb660: "Jas",
        mb670: "1Pet",
        mb680: "2Pet",
        mb690: "1John",
        mb700: "2John",
        mb710: "3John",
        mb720: "Jude",
        mb730: "Rev",
        mb165: "1Esd",
        mb468: "2Esd",
        mb170: "Tob",
        mb171: "Tob",
        mb180: "Jdt",
        mb270: "Wis",
        mb280: "Sir",
        mb305: "PrAzar",
        mb315: "EpJer",
        mb320: "Bar",
        mb325: "Sus",
        mb326: "Sus",
        mb345: "Bel",
        mb346: "Bel",
        mb462: "1Macc",
        mb464: "2Macc",
        mb466: "3Macc",
        mb467: "4Macc",
        mb780: "EpLao",
        mb790: "PrMan",
        mb469: "PrMan",
        mb191: "AddEsth",
        mb231: "Ps151",
        mb232: "PssSol",
        mb235: "PssSol",
        mb800: "Odes",
        mb245: "Odes",
        mb341: "AddDan"
    };
    var abb = abbSBL["mb"+String(b)];
    return abb+" "+c+":"+v;
}

function bookAbbToNo(bookAbb) {
    var bookNo = {
        bGen: "1",
        bExod: "2",
        bLev: "3",
        bNum: "4",
        bDeut: "5",
        bJosh: "6",
        bJudg: "7",
        bRuth: "8",
        b1Sam: "9",
        b2Sam: "10",
        b1Kgs: "11",
        b2Kgs: "12",
        b1Chr: "13",
        b2Chr: "14",
        bEzra: "15",
        bNeh: "16",
        bEsth: "17",
        bJob: "18",
        bPs: "19",
        bProv: "20",
        bEccl: "21",
        bSong: "22",
        bIsa: "23",
        bJer: "24",
        bLam: "25",
        bEzek: "26",
        bDan: "27",
        bHos: "28",
        bJoel: "29",
        bAmos: "30",
        bObad: "31",
        bJonah: "32",
        bMic: "33",
        bNah: "34",
        bHab: "35",
        bZeph: "36",
        bHag: "37",
        bZech: "38",
        bMal: "39",
        bMatt: "40",
        bMark: "41",
        bLuke: "42",
        bJohn: "43",
        bActs: "44",
        bRom: "45",
        b1Cor: "46",
        b2Cor: "47",
        bGal: "48",
        bEph: "49",
        bPhil: "50",
        bCol: "51",
        b1Thess: "52",
        b2Thess: "53",
        b1Tim: "54",
        b2Tim: "55",
        bTitus: "56",
        bPhlm: "57",
        bHeb: "58",
        bJas: "59",
        b1Pet: "60",
        b2Pet: "61",
        b1John: "62",
        b2John: "63",
        b3John: "64",
        bJude: "65",
        bRev: "66",
        bBar: "70",
        bAddDan: "71",
        bPrAzar: "72",
        bBel: "73",
        bSus: "75",
        b1Esd: "76",
        b2Esd: "77",
        bAddEsth: "78",
        bEpJer: "79",
        bJdt: "80",
        b1Macc: "81",
        b2Macc: "82",
        b3Macc: "83",
        b4Macc: "84",
        bPrMan: "85",
        bPs151: "86",
        bSir: "87",
        bTob: "88",
        bWis: "89",
        bPssSol: "90",
        bOdes: "91",
        bEpLao: "92"
    };
    return bookNo["b"+bookAbb];
}

function bcv(b,c,v,opt1,opt2) {
    tbcv(activeText,b,c,v,opt1,opt2);
}

function tbcv(text,b,c,v,opt1,opt2) {
    var verseReference = bcvToVerseRefence(b,c,v);
    if ((opt1 != undefined) && (opt2 != undefined)) {
        if (c == opt1) {
            verseReference = verseReference+"-"+String(opt2);
        } else {
            verseReference = verseReference+"-"+String(opt1)+":"+String(opt2);
        }
    } else if (opt1 != undefined) {
        verseReference = verseReference+"-"+String(opt1);
    }
    document.title = "BIBLE:::"+text+":::"+verseReference;
}

function imv(b,c,v,opt1,opt2) {
    if ((opt1 != undefined) && (opt2 != undefined)) {
        document.title = "_imv:::"+b+"."+c+"."+v+"."+opt1+"."+opt2;
    } else {
        document.title = "_imv:::"+b+"."+c+"."+v;
    }
}

function ctbcv(text,b,c,v) {
    var verseReference = bcvToVerseRefence(b,c,v);
    document.title = "COMMENTARY:::"+text+":::"+verseReference;
}

function cbcv(b,c,v) {
    var verseReference = bcvToVerseRefence(b,c,v);
    document.title = "COMMENTARY:::"+verseReference;
}

function cr(b,c,v) {
    var verseReference = mbbcvToVerseRefence(b,c,v);
    document.title = "BIBLE:::"+activeText+":::"+verseReference;
}

function hl0(id, cl, sn) {
    if (cl != '') {
        w3.addStyle('.c'+cl,'background-color','');
    }
    if (sn != '') {
        w3.addStyle('.G'+sn,'background-color','');
    }
    if (id != '') {
        var focalElement = document.getElementById('w'+id);
        if (focalElement != null) {
            document.getElementById('w'+id).style.background='';
        }
    }
}

function w(book, wordID) {
    document.title = "WORD:::"+book+":::"+wordID;
}

function iw(book, wordID) {
    if (book != '' && wordID != '') {
        document.title = "_instantWord:::"+book+":::"+wordID;
    }
}

function qV(v) {
    document.title = "_instantVerse:::"+activeText+":::"+activeB+"."+activeC+"."+v;
}

function mV(v) {
    document.title = "_menu:::"+activeText+"."+activeB+"."+activeC+"."+v;
}

function nV(v) {
    document.title = "_openversenote:::"+activeB+"."+activeC+"."+v;
}

function nC() {
    document.title = "_openchapternote:::"+activeB+"."+activeC;
}

function luV(v) {
    var verseReference = bcvToVerseRefence(activeB,activeC,v);
    document.title = "_stayOnSameTab:::";
    document.title = "BIBLE:::"+activeText+":::"+verseReference;
}

function luW(v,wid,cl,lex,morph,bdb) {
    document.title = "WORD:::"+activeB+":::"+wid;
}

function checkCompare() {
    versionList.forEach(addCompare);
    if (compareList.length == 0) {
        alert("No version is selected for comparison.");
    } else {
        var compareTexts = compareList.join("_");
        compareList = [];
        var verseReference = bcvToVerseRefence(activeB,activeC,activeV);
        document.title = "COMPARE:::"+activeText+"_"+compareTexts+":::"+verseReference;
    }
}

function addCompare(value) {
    var checkBox = document.getElementById("compare"+value);
    if (checkBox.checked == true){
        compareList.push(value);
    }
}

function checkParallel() {
    versionList.forEach(addParallel);
    if (parallelList.length == 0) {
        alert("No version is selected for parallel reading.");
    } else {
        var parallelTexts = parallelList.join("_");
        parallelList = [];
        var verseReference = bcvToVerseRefence(activeB,activeC,activeV);
        document.title = "PARALLEL:::"+activeText+"_"+parallelTexts+":::"+verseReference;
    }
}

function addParallel(value) {
    var checkBox = document.getElementById("parallel"+value);
    if (checkBox.checked == true){
        parallelList.push(value);
    }
}

function checkDiff() {
    versionList.forEach(addDiff);
    if (diffList.length == 0) {
        alert("No version is selected for detailed comparison.");
    } else {
        var diffTexts = diffList.join("_");
        diffList = [];
        var verseReference = bcvToVerseRefence(activeB,activeC,activeV);
        document.title = "DIFF:::"+activeText+"_"+diffTexts+":::"+verseReference;
    }
}

function addDiff(value) {
    var checkBox = document.getElementById("diff"+value);
    if (checkBox.checked == true){
        diffList.push(value);
    }
}

function checkSearch(searchKeyword, searchText) {
    var searchString = document.getElementById("bibleSearch").value;
    if (searchString == "") {
        alert("Search field is empty!");
    } else {
        document.title = searchKeyword+":::"+searchText+":::"+searchString;
    }
}

function checkMultiSearch(searchKeyword) {
    var searchString = document.getElementById("multiBibleSearch").value;
    if (searchString == "") {
        alert("Search field is empty!");
    } else {
        versionList.forEach(addMultiSearch);
        if (searchList.length == 0) {
            document.title = searchKeyword+":::"+activeText+":::"+searchString;
        } else {
            var searchTexts = searchList.join("_");
            searchList = [];
            document.title = searchKeyword+":::"+searchTexts+":::"+searchString;
        }
    }
}

function addMultiSearch(value) {
    var checkBox = document.getElementById("search"+value);
    if (checkBox.checked == true){
        searchList.push(value);
    }
}

function searchLexicalEntry(lexicalEntry) {
    document.title = "LEMMA:::"+lexicalEntry;
}

function searchCode(lexicalEntry, morphologyCode) {
    document.title = "MORPHOLOGYCODE:::"+lexicalEntry+","+morphologyCode;
}

function searchMorphologyCode(lexicalEntry, morphologyCode) {
    document.title = "MORPHOLOGYCODE:::"+lexicalEntry+","+morphologyCode;
}

function searchMorphologyItem(lexicalEntry, morphologyItem) {
    document.title = "MORPHOLOGY:::LexicalEntry LIKE '%"+lexicalEntry+",%' AND Morphology LIKE '%"+morphologyItem+"%'";
}

function searchBook(lexicalEntry, bookName) {
    bookNo = bookAbbToNo(bookName);
    document.title = "MORPHOLOGY:::LexicalEntry LIKE '%"+lexicalEntry+",%' AND Book = "+bookNo;
}

function lmCombo(lexicalEntry, morphologyModule, morphologyCode) {
    document.title = "LMCOMBO:::"+lexicalEntry+":::"+morphologyModule+":::"+morphologyCode;
}

function lexicon(module, entry) {
    document.title = "LEXICON:::"+module+":::"+entry;
}

function lex(entry) {
    document.title = "LEXICON:::"+entry;
}

function bdbid(entry) {
    document.title = "LEXICON:::BDB:::"+entry;
}

function lgntdf(entry) {
    document.title = "LEXICON:::LGNTDF:::"+entry;
}

function gk(entry) {
    var initial = entry[0];
    var number = entry.slice(1);
    if (number.length == 1) {
        number = "000"+number;
    } else if (number.length == 2) {
        number = "00"+number;
    } else if (number.length == 3) {
        number = "0"+number;
    }
    document.title = "LEXICON:::gk"+initial+"5"+number;
}

function ln(entry) {
    document.title = "LEXICON:::ln"+entry;
}

function encyclopedia(module, entry) {
    document.title = "ENCYCLOPEDIA:::"+module+":::"+entry;
}

function cl(entry) {
	if (typeof activeB !== 'undefined' || activeB !== null) {
    	var bcv = activeB+'.'+activeC+'.'+activeV;
    	clause(bcv, entry);
	}
}

function clause(bcv, entry) {
    document.title = "CLAUSE:::"+bcv+":::"+entry;
}

function bibleDict(entry) {
    document.title = "DICTIONARY:::"+entry;
}

function searchBibleBook(text, book, searchString) {
    document.title = "ADVANCEDSEARCH:::"+text+":::Book = "+book+" AND Scripture LIKE '%"+searchString+"%'";
}

function iSearchBibleBook(text, book, searchString) {
    document.title = "ADVANCEDISEARCH:::"+text+":::Book = "+book+" AND Scripture LIKE '%"+searchString+"%'";
}

function exlbl(entry) {
    document.title = "EXLB:::exlbl:::"+entry;
}

function exlbp(entry) {
    document.title = "EXLB:::exlbp:::"+entry;
}

function exlbt(entry) {
    document.title = "EXLB:::exlbt:::"+entry;
}

function openImage(module, entry) {
    document.title = "_image:::"+module+":::"+entry;
    document.title = "UniqueBible.app";
}

function searchResource(tool) {
    if (tool != "") {
        document.title = "_command:::SEARCHTOOL:::"+tool+":::";
    }
}

function searchDict(module) {
    searchResource(module);
}

function searchDictionary(module) {
    searchResource(module);
}

function searchEncyc(module) {
    searchResource(module);
}

function searchEncyclopedia(module) {
    searchResource(module);
}

function searchItem(module, entry) {
    document.title = "SEARCHTOOL:::"+module+":::"+entry;
}

function searchEntry(module, entry) {
    document.title = "SEARCHTOOL:::"+module+":::"+entry;
}

function rmac(entry) {
    searchItem("mRMAC", entry);
}

function etcbcmorph(entry) {
    searchItem("mETCBC", entry);
}

function lxxmorph(entry) {
    searchItem("mLXX", entry);
}

function listBookTopic(module) {
    document.title = "_book:::"+module;
}

function openHistoryRecord(recordNo) {
    document.title = "_historyrecord:::"+recordNo;
}

function openExternalRecord(recordNo) {
    document.title = "_openfile:::"+recordNo;
}

function openHtmlFile(filename) {
    document.title = "open:::htmlResources/"+filename;
}

function openHtmlImage(filename) {
    document.title = "_htmlimage:::"+filename;
}

function editExternalRecord(recordNo) {
    document.title = "_editfile:::"+recordNo;
}

function website(link) {
    document.title = "_website:::"+link;
}

function searchThirdDictionary(module, entry) {
    document.title = "SEARCHTHIRDDICTIONARY:::"+module+":::"+entry;
}

function openThirdDictionary(module, entry) {
    document.title = "THIRDDICTIONARY:::"+module+":::"+entry;
}

function uba(file) {
    document.title = "_uba:::"+file;
}

function bn(b, c, v, n) {
    document.title = "_biblenote:::"+b+"."+c+"."+v+"."+n;
}

function wordnote(module, wordID) {
    document.title = "_wordnote:::"+module+":::"+wordID;
}

function searchBible(module, item) {
    document.title = "SEARCH:::"+module+":::"+item;
}

function searchVerse(module, item, b, c, v) {
    document.title = "ADVANCEDSEARCH:::"+module+":::Book = "+b+" AND Chapter = "+c+" AND Verse = "+v+" AND Scripture LIKE '%"+item+"%'";
}

function searchWord(portion, wordID) {
    document.title = "_searchword:::"+portion+":::"+wordID;
}

function harmony(tool, number) {
    document.title = "_harmony:::"+tool+"."+number;
}

function promise(tool, number) {
    document.title = "_promise:::"+tool+"."+number;
}

function openMarvelFile(filename) {
    document.title = "_open:::"+filename;
}

function hiV(b,c,v,code) {
    spanId = "s" + b + "." + c + "." + v
    divEl = document.getElementById(spanId);
    curClass = divEl.className;
    if (code === "delete") {
        divEl.className = "";
    } else if (code === curClass) {
        divEl.className = "";
        code = "delete";
    } else {
        divEl.className = code;
    }
    verseReference = bcvToVerseRefence(b,c,v);
    document.title = "_HIGHLIGHT:::"+verseReference+":::"+code;
}