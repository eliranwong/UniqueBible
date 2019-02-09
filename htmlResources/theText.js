function textName(name) {
    var fullname = getFullTextName(name);
    document.title = "_info:::"+fullname;
}

function getFullTextName(abbreviation) {
    var fullTextNameObject = {
        tAMP: "Amplified Bible",
        tAMPC: "Amplified Bible, Classic Edition",
        tASV: "American Standard Version",
        tBBE: "Bible in Basic English",
        tBSB: "Berean Study Bible",
        tCCB: "Contemporary Chinese Bible",
        tCEB: "Common English Bible",
        tCEV: "Contemporary English Version",
        tCSB: "Christian Standard Bible",
        tCUV: "Chinese Union Version",
        tCUVs: "Chinese Union Version (simplified Chinese)",
        tERV: "English Revised Version",
        tESV: "English Standard Version",
        tEXP: "Expanded Bible",
        tISV: "International Standard Version",
        tKJV: "King James Version",
        tLEB: "Lexham English Bible",
        tLXX: "LXX / Septuagint (in KJV versification)",
        tLXX1: "LXX / Septuagint [main text]",
        tLXX1i: "LXX / Septuagint Interlinear [main text]",
        tLXX2: "LXX / Septuagint [alternate text]",
        tLXX2i: "LXX / Septuagint interlinear [alternate text]",
        tMAB: "Marvel Annotated Bible",
        tMIB: "Marvel Interlinear Bible",
        tMOB: "Marvel Original Bible",
        tMPB: "Marvel Parallel Bible",
        tMSG: "The Message",
        tMTB: "Marvel Trilingual Bible",
        tMounce: "Mounce's New Testament",
        tNAS: "New American Standard Bible",
        tNET: "New English Translation",
        tNETS: "New English Translation of the Septuagint",
        tNIV: "New International Version",
        tNJPS: "New Jewish Publication Society of America Tanakh",
        tNKJ: "New King James Version",
        tNLT: "New Living Translation",
        tNRS: "New Revised Standard Version",
        tNTW: "N.T. Wright's New Testament",
        tOHGB: "Open Hebrew-Greek Bible",
        tOHGBi: "Open Hebrew-Greek Bible [interlinear]",
        tRCUV: "Revised Chinese Union Version",
        tRSV: "Revised Standard Version",
        tTNK: "Tanak",
        tTPT: "The Passion Translation",
        tULT: "Unlocked Literal Text",
        tUST: "Unlocked Simplified Text",
        tWEB: "World English Bible",
        tYLT: "Young's Literal Translation"
    };
    return fullTextNameObject["t"+abbreviation];
}

function commentaryName(name) {
    var fullname = getFullCommentaryName(name);
    document.title = "_info:::"+fullname;
}

function getFullCommentaryName(abbreviation) {
    var fullCommentaryNameObject = {
        cBarnes: "Notes on the Old and New Testaments (Barnes) [26 vol.]",
        cBenson: "Commentary on the Old and New Testaments (Benson) [5 vol.]",
        cBI: "Biblical Illustrator (Exell) [58 vol.]",
        cBrooks: "Complete Summary of the Bible (Brooks) [2 vol.]",
        cCalvin: "John Calvin's Commentaries (Calvin) [22 vol.]",
        cClarke: "Commentary on the Bible (Clarke) [6 vol.]",
        cCBSC: "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]",
        cCECNT: "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]",
        cCGrk: "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]",
        cCHP: "Church Pulpit Commentary (Nisbet) [12 vol.]",
        cCPBST: "College Press Bible Study Textbook Series (College) [59 vol.]",
        cEBC: "Expositor's Bible Commentary (Nicoll) [49 vol.]",
        cECER: "Commentary for English Readers (Ellicott) [8 vol.]",
        cEGNT: "Expositor's Greek New Testament (Nicoll) [5 vol.]",
        cGCT: "Greek Testament Commentary (Alford) [4 vol.]",
        cGill: "Exposition of the Entire Bible (Gill) [9 vol.]",
        cHenry: "Exposition of the Old and New Testaments (Henry) [6 vol.]",
        cHH: "Horæ Homileticæ (Simeon) [21 vol.]",
        cICCNT: "International Critical Commentary, NT (1896-1929) [16 vol.]",
        cJFB: "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]",
        cKD: "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]",
        cLange: "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]",
        cMacL: "Expositions of Holy Scripture (MacLaren) [32 vol.]",
        cPHC: "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]",
        cPulpit: "Pulpit Commentary (Spence) [23 vol.]",
        cRob: "Word Pictures in the New Testament (Robertson) [6 vol.]",
        cSpur: "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]",
        cVincent: "Word Studies in the New Testament (Vincent) [4 vol.]",
        cWesley: "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]",
        cWhedon: "Commentary on the Old and New Testaments (Whedon) [14 vol.]"
    };
    return fullCommentaryNameObject["c"+abbreviation];
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
    var SBLabb = ["", "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas", "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev"];
    var abb = SBLabb[b];
    return abb+" "+c+":"+v;
}

function mbbcvToVerseRefence(b,c,v) {
    var MBBkList = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 190, 220, 230, 240, 250, 260, 290, 300, 310, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710, 720, 730];
    var b2 = MBBkList.indexOf(b);
    var SBLabb = ["Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas", "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev"];
    var abb = SBLabb[b2];
    return abb+" "+c+":"+v;
}

function tbcv(text,b,c,v) {
    var verseReference = bcvToVerseRefence(b,c,v);
    document.title = "BIBLE:::"+text+":::"+verseReference;
}

function bcv(b,c,v) {
    var verseReference = bcvToVerseRefence(b,c,v);
    document.title = "BIBLE:::"+activeText+":::"+verseReference;
}

function cr(b,c,v) {
    var verseReference = mbbcvToVerseRefence(b,c,v);
    document.title = "BIBLE:::"+activeText+":::"+verseReference;
}

function hl1(id, cl, sn) {
    if (cl != '') {
        w3.addStyle('.c'+cl,'background-color','PAPAYAWHIP');
    }
    if (sn != '') {
        w3.addStyle('.G'+sn,'background-color','#E7EDFF');
    }
    if (id != '') {
        var focalElement = document.getElementById('w'+id);
        if (focalElement != null) {
            document.getElementById('w'+id).style.background='#C9CFFF';
        }
    }
    if (id != '') {
        document.title = "_instantWord:::"+activeB+":::"+id;
    }
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

function luV(v) {
    var verseReference = bcvToVerseRefence(activeB,activeC,v);
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
    document.title = "LEXICON:::gk"+entry;
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

function exlbt(entry) {
    document.title = "TOPIC:::"+entry;
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
