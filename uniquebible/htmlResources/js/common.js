/* Copy text to clipboard */

function copyTextToClipboard(text) {
  
    /* Copy the text inside the text field */
    navigator.clipboard.writeText(text);
    
    /* Alert the copied text */
    alert("Copied " + "'" + text + "'");
}

/* SECTION - SCROLLING BIBLES */

function scrollBibles() {
    if ((getMobileOperatingSystem() != 'iOS') && (window.parent.paraWin == 2) && (window.parent.paraContent == 'bible') && (window.parent.syncBible == 1)) {
    
    var bibleFrame = window.parent.document.getElementById('bibleFrame');
    var bibleDoc = bibleFrame.contentDocument || iframe.contentWindow.document;
    var bibleLastElement = bibleDoc.getElementById('footer');
    var bibleHeight = bibleLastElement.offsetTop;
    
    var toolFrame = window.parent.document.getElementById('toolFrame');
    var toolDoc = toolFrame.contentDocument || iframe.contentWindow.document;
    var toolLastElement = toolDoc.getElementById('footer');
    var toolHeight = toolLastElement.offsetTop;
    
    var verticalPos = window.pageYOffset || (document.documentElement || document.body.parentNode || document.body).scrollTop;
    var paraPos;
    
        if ((window.self == bibleFrame.contentWindow) && (window.parent.currentZone == 2)) {
        window.parent.currentZone = 0;
        }
        else if ((window.self == toolFrame.contentWindow) && (window.parent.currentZone == 1)) {
        window.parent.currentZone = 0;
        }
        else {
            if (window.self == bibleFrame.contentWindow) { window.parent.currentZone = 1 }
            else if (window.self == toolFrame.contentWindow) { window.parent.currentZone = 2 }
        }
    
        if ((window.self == bibleFrame.contentWindow) && (verticalPos < bibleHeight) && (window.parent.currentZone == 1)) {
        paraPos =  (verticalPos / bibleHeight) * toolHeight;
        paraPos = Math.round(paraPos);
        toolFrame.contentWindow.scrollTo(0,paraPos);
        }
        else if ((window.self == toolFrame.contentWindow) && (verticalPos < toolHeight) && (window.parent.currentZone == 2)) {
        paraPos =  (verticalPos / toolHeight) * bibleHeight;
        paraPos = Math.round(paraPos);
        bibleFrame.contentWindow.scrollTo(0,paraPos);
        }
    }
}
    
function scrollBiblesIOS(id) {
    
    var bibleDiv = document.getElementById('bibleDiv');
    var bibleFrame = document.getElementById('bibleFrame');
    var bibleDoc = bibleFrame.contentDocument || iframe.contentWindow.document;
    var bibleLastElement = bibleDoc.getElementById('footer');
    var bibleHeight = bibleLastElement.offsetTop;
    
    var toolDiv = document.getElementById('toolDiv');
    var toolFrame = document.getElementById('toolFrame');
    var toolDoc = toolFrame.contentDocument || iframe.contentWindow.document;
    var toolLastElement = toolDoc.getElementById('footer');
    var toolHeight = toolLastElement.offsetTop;
    
    var verticalPos = document.getElementById(id).scrollTop;
    var paraPos;
    
    if ((id == 'bibleDiv') && (verticalPos > bibleHeight)) { document.getElementById(id).scrollTop = bibleHeight; }
    if ((id == 'toolDiv') && (verticalPos > toolHeight)) { document.getElementById(id).scrollTop = toolHeight; }
    
    if ((getMobileOperatingSystem() == 'iOS') && (paraWin == 2) && (paraContent == 'bible') && (syncBible == 1)) {
    
        if ((id == 'bibleDiv') && (currentZone == 2)) {
        currentZone = 0;
        }
        else if ((id == 'toolDiv') && (currentZone == 1)) {
        currentZone = 0;
        }
        else {
            if (id == 'bibleDiv') { currentZone = 1 }
            else if (id == 'toolDiv') { currentZone = 2 }
        }
    
        if ((id == 'bibleDiv') && (verticalPos < bibleHeight) && (currentZone == 1)) {
        paraPos =  (verticalPos / bibleHeight) * toolHeight;
        paraPos = Math.round(paraPos);
        document.getElementById('toolDiv').scrollTop = paraPos;
        }
        if ((id == 'toolDiv') && (verticalPos < toolHeight) && (currentZone == 2)) {
        paraPos =  (verticalPos / toolHeight) * bibleHeight;
        paraPos = Math.round(paraPos);
        document.getElementById('bibleDiv').scrollTop = paraPos;
        }
    }
}
/* SECTION - LOADING A SPECIFIC BIBLE VERSE
*/

function openBibleVerse(id,b,c,v,module) {
    bcvId = 'v' + b + '.' + c + '.' + v;
    document.getElementById(id).src = 'main.html#' + bcvId;
}

function loadBible() {
    //document.getElementById("footer").innerHTML = getFooter3();
    window.addEventListener("scroll", scrollBibles);
    
    var bibleFrame = window.parent.document.getElementById('bibleFrame');
    var toolFrame = window.parent.document.getElementById('toolFrame');
    //var info = window.location.href;
    if (window.self == bibleFrame.contentWindow) { 
        // check matching src and href
        // workaround for iOS scrolling
        // bibleFrame.src = info;
        //if (bibleFrame.src != info) { bibleFrame.src = info; }
        //if (bibleFrame.contentWindow.location.href != info) { bibleFrame.contentWindow.location.href = info; }
        // mod info
        //window.parent.activeText = activeText;
        //window.parent.tempActiveText = activeText;
        // verse info
        //var patt = /#v.*$/g;
        //info = info.match(patt).toString().slice(2);
        //var bcv = info.split(".");
        /*window.parent.activeB = Number(bcv[0]);
        window.parent.tempB = window.parent.activeB;
        window.parent.activeC = Number(bcv[1]);
        window.parent.tempC = window.parent.activeC;
        window.parent.activeV = Number(bcv[2]);
        window.parent.tempV = window.parent.activeV;*/
        // window.parent.updateBibleTitle();
        // window.parent.history.pushState(null, null, '/index.html?' + window.parent.activeText + '&' + window.parent.activeB + '.' + window.parent.activeC + '.' + window.parent.activeV);
        window.parent.resizeSite();
    	// BibleSync
    	if ((window.parent.paraWin == 2) && (window.parent.syncBible == 1) && (window.parent.paraContent == 'bible')) { window.parent.checkSync('bibleFrame',window.parent.activeB); }
    	if ((window.parent.paraWin == 2) && (window.parent.syncBible == 1) && (window.parent.paraContent == 'bible')) { 
    		switch(window.parent.triggerPara) {
        	case 0:
        	window.parent.triggerPara = 1;
        	window.parent.openBibleVerse('toolFrame',window.parent.activeB,window.parent.activeC,window.parent.activeV);
        	break;
        	case 1:
        	window.parent.triggerPara = 0;
        	break;
        	}
    	}
    } else if (window.self == toolFrame.contentWindow) {
        // check matching src and href
        // workaround for iOS scrolling
        //toolFrame.src = info;
        //if (toolFrame.src != info) { toolFrame.src = info; }
        //if (toolFrame.contentWindow.location.href != info) { toolFrame.contentWindow.location.href = info; }
        // workaround for iOS
        if (getMobileOperatingSystem() == 'iOS') { window.parent.document.getElementById('bibleDiv').scrollTop = window.parent.document.getElementById('bibleDiv').scrollTop - 1; }
        // get book number
        /*window.parent.toolB = window.parent.tempB;
        window.parent.toolC = window.parent.tempC;
        window.parent.toolV = window.parent.tempV;
        window.parent.tempActiveText = window.parent.activeText;
        window.parent.tempB = window.parent.activeB;
        window.parent.tempC = window.parent.activeC;
        window.parent.tempV = window.parent.activeV;*/
        // set tool window info
        window.parent.paraContent = 'bible';
        //window.parent.document.getElementById('syncOption').style.display='';
        window.parent.resizeSite();
    	// BibleSync
    	if (window.parent.syncBible == 1) { window.parent.checkSync('toolFrame', window.parent.toolB); }
    	if (window.parent.syncBible == 1) { 
    		switch(window.parent.triggerPara) {
        	case 0:
        	window.parent.triggerPara = 1;
        	window.parent.openBibleVerse('bibleFrame', window.parent.toolB, window.parent.toolC, window.parent.toolV);
        	break;
        	case 1:
        	window.parent.triggerPara = 0;
        	break;
        	}
    	}
    }
}

function checkSync(source,b,module) {
var target; var module;
if (source == 'bibleFrame') { target = document.getElementById('toolFrame'); }
else if (source == 'toolFrame') { target = document.getElementById('bibleFrame'); }

	if (module == undefined) { module = target.contentWindow.activeText; }

var alertTitle = '<h3>"Bible Sync" is turned "OFF"</h3>';
var alertSyncBibleOff = '<p>One of opened bible versions does not have the passage you had just selected.</p><p>To prevent errors on synchronising bibles, option "Bible Sync" is now automatically turned "OFF".</p><p>You may re-activate "Bible Sync" manually via our navigation menu.</p>';

	if (module == 'lxx2' || module == 'lxx2i') {
	var lxx2Bk = [60, 70, 340, 170, 325, 345];
	if (lxx2Bk.indexOf(b) < 0) { syncSwitch(); messageUser(alertTitle, alertSyncBibleOff); }
	}
	else if (b < 470 || b > 730) {
	var NTonly = ['nestle1904', 'nestle1904i', 'sblgntc', 'bgb', 'bib', 'bgb_blb', 'bgb_bsb', 'tr_kjv', 'byz_web', 'wh_cuv', 'blb', 'bsb'];
	if (NTonly.indexOf(module) >= 0) { syncSwitch(); messageUser(alertTitle, alertSyncBibleOff); }
	}
	else if (b >= 470 || b <= 730) {
	var OTonly = ['bhs', 'bhsl', 'bhsi', 'bhs_kjv', 'bhs_wrv', 'bhs_web', 'bhs_leb', 'bhs_cuv', 'lxx2012', 'lxx1', 'lxx2', 'lxx1i', 'lxx2i'];
	if (OTonly.indexOf(module) >= 0) { syncSwitch(); messageUser(alertTitle, alertSyncBibleOff); }
	}
}

/* START - FIXING iOS SCROLLING ISSUES */

function getMobileOperatingSystem() {
    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    // Windows Phone must come first because its UA also contains "Android"
    if (/windows phone/i.test(userAgent)) {
        return "Windows Phone";
    }
    if (/android/i.test(userAgent)) {
        return "Android";
    }
    // iOS detection from: http://stackoverflow.com/a/9039885/177710
    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
        return "iOS";
    }
    return "unknown";
}

function resizeSite() {
    // For iPhone ONLY, if ((/iPhone|iPod/.test(navigator.userAgent)) && (!window.MSStream)) { }
    if (getMobileOperatingSystem() == 'iOS') { disableIOSScrolling(); }
    
    var screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    
    var screenHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
    if (screenWidth >= screenHeight) {landscape = 1;}
    else if (screenHeight >= screenWidth) {landscape = 0;}
    
    var contentHeight = screenHeight - 52;
    
    var addSpace;
    if ((landscape == 0) && (paraWin == 2)) {addSpace = (contentHeight / 2) - 110;}
    else {addSpace = contentHeight - 110;}
    if (addSpace <= 0) {addSpace = 1;}
    
    var bibleFrame = document.getElementById('bibleFrame');
    var bibleDoc = bibleFrame.contentDocument || bibleFrame.contentWindow.document;
    var bibleLastElement = bibleDoc.getElementById('lastElement');
    if (bibleLastElement) {
        bibleLastElement.style.display = 'block';
        bibleLastElement.style.height = addSpace + 'px';
    }
    if (getMobileOperatingSystem() == 'iOS') { 
        var bBODY = bibleDoc.body; var bHTML = bibleDoc.documentElement;
        var bHeight = Math.max( bBODY.scrollHeight, bBODY.offsetHeight, bHTML.clientHeight, bHTML.scrollHeight, bHTML.offsetHeight );
        bibleFrame.height = bHeight;
        bibleFrame.style.height = bHeight + 'px';
    }
    
    var toolFrame = document.getElementById('toolFrame');
    var toolDoc = toolFrame.contentDocument || toolFrame.contentWindow.document;
    if ((paraWin == 2) && (paraContent == 'bible')) {
    var toolLastElement = toolDoc.getElementById('lastElement');
    toolLastElement.style.display = 'block';
    toolLastElement.style.height = addSpace + 'px';
    }
    if (getMobileOperatingSystem() == 'iOS') { 
        var tBODY = toolDoc.body; var tHTML = toolDoc.documentElement;
        var tHeight = Math.max( tBODY.scrollHeight, tBODY.offsetHeight, tHTML.clientHeight, tHTML.scrollHeight, tHTML.offsetHeight );
        toolFrame.height = tHeight;
        toolFrame.style.height = tHeight + 'px';
    }
    
    var bibleDiv = document.getElementById('bibleDiv');
    var toolDiv = document.getElementById('toolDiv');

    switch(paraWin) {
        case 1:
        bibleDiv.style.borderBottom = 'none';
        toolDiv.style.borderTop = 'none';
        bibleDiv.style.width = screenWidth + 'px';
        bibleDiv.style.height = contentHeight + 'px';
        break;
        case 2:
        if (landscape == 1) {
        bibleDiv.style.borderBottom = 'none';
        toolDiv.style.borderTop = 'none';
        bibleDiv.style.width = (screenWidth / 2) + 'px';
        toolDiv.style.width = (screenWidth / 2) + 'px';
        bibleDiv.style.height = contentHeight + 'px';
        toolDiv.style.height = contentHeight + 'px';
        }
        else if (landscape == 0) {
        bibleDiv.style.width = screenWidth + 'px';
        toolDiv.style.width = screenWidth + 'px';
        bibleDiv.style.height = ((contentHeight - 4) / 2) + 'px';
        toolDiv.style.height = ((contentHeight - 4) / 2) + 'px';
        bibleDiv.style.borderBottom = '2px solid lightgrey';
        toolDiv.style.borderTop = '2px solid lightgrey';
        }
        break;
    }
    
    if (getMobileOperatingSystem() == 'iOS') { setTimeout(enableIOSScrolling,100); }
    
    // align content in view
    setTimeout(function() {
    if (activeB != undefined) { fixBibleVerse(); }
    if ((paraWin == 2) && (paraContent == 'tool')) {
        if (getMobileOperatingSystem() == 'iOS') {toolDiv.scrollTop = 0;}
        else {toolFrame.contentWindow.scrollTo(0,0);}
    }
    else if ((paraWin == 2) && (paraContent == 'bible') && (syncBible == 0)) {
        fixToolVerse(toolB,toolC,toolV);
    }
    },500); 
    
    // workaround for iPhone; problem: navigation bar hide under "tabs" after changing from portrait to landscape
    setTimeout(function(){window.scrollTo(0, 1);}, 500);
}
  
function enableIOSScrolling() {
    var contentDiv = document.getElementById("content");
    var bibleDiv = document.getElementById("bibleDiv");
    var toolDiv = document.getElementById("toolDiv");
    contentDiv.style.overflowY = "scroll";
    contentDiv.style.overflowX = "auto";
    bibleDiv.style.overflowY = "scroll";
    bibleDiv.style.overflowX = "auto";
    toolDiv.style.overflowY = "scroll";
    toolDiv.style.overflowX = "auto";
    contentDiv.style.webkitOverflowScrolling = "touch";
    bibleDiv.style.webkitOverflowScrolling = "touch";
    toolDiv.style.webkitOverflowScrolling = "touch";
}
  
function disableIOSScrolling() {
    var contentDiv = document.getElementById("content");
    var bibleDiv = document.getElementById("bibleDiv");
    var toolDiv = document.getElementById("toolDiv");
    contentDiv.style.overflow = "auto";
    bibleDiv.style.overflow = "auto";
    toolDiv.style.overflow = "auto";
    contentDiv.style.webkitOverflowScrolling = "auto";
    bibleDiv.style.webkitOverflowScrolling = "auto";
    toolDiv.style.webkitOverflowScrolling = "auto";
}

// There is a known issue about getting offset of an element within a table:
// https://stackoverflow.com/questions/1044988/getting-offsettop-of-element-in-a-table
function getOffsetByElement(elem) {
    if (!elem) elem = this;
    var x = elem.offsetLeft;
    var y = elem.offsetTop;
    while (elem = elem.offsetParent) {
        x += elem.offsetLeft;
        y += elem.offsetTop;
    }
    return { left: x, top: y };
}

function fixBibleVerse() {
    var targetPos = 'v' + activeB + '.' + activeC + '.' + activeV;
    var targetFrame = document.getElementById('bibleFrame');
    var targetDoc = targetFrame.contentDocument || targetFrame.contentWindow.document;
    var targetElement = targetDoc.getElementById(targetPos);
    //var targetHeight = targetElement.offsetTop;
    var targetHeight = getOffsetByElement(targetElement).top
    if (getMobileOperatingSystem() == 'iOS') { document.getElementById('bibleDiv').scrollTop = targetHeight; }
    else {targetFrame.contentWindow.scrollTo(0,targetHeight);}
}
  
function fixToolVerse(b,c,v) {
    var targetPos = 'v' + b + '.' + c + '.' + v;
    var targetFrame = document.getElementById('toolFrame');
    var targetDoc = targetFrame.contentDocument || targetFrame.contentWindow.document;
    var targetElement = targetDoc.getElementById(targetPos);
    //var targetHeight = targetElement.offsetTop;
    var targetHeight = getOffsetByElement(targetElement).top
    if (getMobileOperatingSystem() == 'iOS') { document.getElementById('toolDiv').scrollTop = targetHeight; }
    else {targetFrame.contentWindow.scrollTo(0,targetHeight);}
}

/* END - FIXING iOS SCROLLING ISSUES */

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

function instantInfo(text) {
    document.title = "_info:::"+text;
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
    //tbcv(activeText,b,c,v,opt1,opt2);
    tbcv("",b,c,v,opt1,opt2);
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
    if (text == "") {
        document.title = "BIBLE:::"+verseReference;
    } else {
        document.title = "BIBLE:::"+text+":::"+verseReference;
    }
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

function ohgbi(b, c, v, wordID) {
    document.title = "_instantVerse:::"+b+"."+c+"."+v+"."+wordID;
}

function qV(v) {
    document.title = "_instantVerse:::"+activeText+":::"+activeB+"."+activeC+"."+v;
}

function mV(v) {
    document.title = "_vndc:::"+activeText+"."+activeB+"."+activeC+"."+v;
}

function nV(v) {
    document.title = "_openversenote:::"+activeB+"."+activeC+"."+v;
}

function nC() {
    document.title = "_openchapternote:::"+activeB+"."+activeC;
}

function nB() {
    document.title = "_openbooknote:::"+activeB;
}

function rC(text, startVerse) {
    if (startVerse == undefined) {
        document.title = "READCHAPTER:::"+text+"."+activeB+"."+activeC;
    } else {
        document.title = "READCHAPTER:::"+text+"."+activeB+"."+activeC+"."+startVerse;
    }
    
}

function rV(text, v) {
    document.title = "READVERSE:::"+text+"."+activeB+"."+activeC+"."+v;
}

function ld(lexicalEntry) {
    document.title = "_lexicaldata:::"+lexicalEntry;
}

function luV(v) {
    var verseReference = bcvToVerseRefence(activeB,activeC,v);
    document.title = "_stayOnSameTab:::";
    // document.title = "BIBLE:::"+activeText+":::"+verseReference;
    document.title = "_vnsc:::"+activeText+"."+activeB+"."+activeC+"."+v+"."+verseReference;
}

function luW(v,wid,cl,lex,morph,bdb) {
    document.title = "WORD:::"+activeB+":::"+wid;
}

function wah(v,wid) {
    document.title = "READWORD:::BHS5."+activeB+"."+activeC+"."+v+"."+wid;
}

function wag(v,wid) {
    document.title = "READWORD:::OGNT."+activeB+"."+activeC+"."+v+"."+wid;
}

function wahl(v,wid) {
    document.title = "READLEXEME:::BHS5."+activeB+"."+activeC+"."+v+"."+wid;
}

function wagl(v,wid) {
    document.title = "READLEXEME:::OGNT."+activeB+"."+activeC+"."+v+"."+wid;
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
        document.title = "DIFFERENCE:::"+activeText+"_"+diffTexts+":::"+verseReference;
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
        alert("Search input is empty!");
    } else {
        document.title = searchKeyword+":::"+searchText+":::"+searchString;
    }
}

function openBibleMap() {
    var searchString = document.getElementById("mapReference").value;
    document.title = "MAP:::"+searchString;
}

function checkMultiSearch(searchKeyword) {
    var searchString = document.getElementById("multiBibleSearch").value;
    if (searchString == "") {
        alert("Search input is empty!");
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

function checkComparison(keyword) {
    versionList.forEach(addMultiSearch);
    if (searchList.length == 0) {
        alert("Select bible versions first!");
    } else {
        var texts = searchList.join("_");
        searchList = [];
        var verseReference = bcvToVerseRefence(activeB,activeC,activeV);
        document.title = keyword+":::"+texts+":::"+verseReference;
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

function concord(entry) {
    document.title = "CONCORDANCE:::"+entry;
}

function concordance(module, entry) {
    document.title = "CONCORDANCE:::"+module+":::"+entry;
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
    document.title = "_biblenote:::"+activeText+":::"+b+"."+c+"."+v+"."+n;
}

function wordnote(module, wordID) {
    document.title = "_wordnote:::"+module+":::"+wordID;
}

function searchBible(module, item) {
    document.title = "COUNT:::"+module+":::"+item;
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
    document.title = "_HIGHLIGHT:::"+code+":::"+verseReference;
}

function jump(anchor){
    window.location.href = "#"+anchor;
}
