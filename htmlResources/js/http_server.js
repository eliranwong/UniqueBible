/* Onload functions */

function onBodyLoad() {
    cmd = decodeURIComponent(location.search);
    cmd = cmd.replace("?cmd=", "")
             .replace("+", " ");
    el = document.getElementById('commandInput')
    el2 = document.getElementById('commandInputHolder')
    if (cmd != "") {
        el.value = cmd
        el2.title = cmd
    }
    el.focus();
}

function adjustBibleDivWidth(adjust) {
    var bibleDiv = document.getElementById('bibleDiv');
    bibleDiv.style.setProperty('width', 'calc(100% - ' + adjust + ')');
}

/* Display message */
function messageUser(messageHeader, message) {
    document.getElementById('myMessageHeader').innerHTML = messageHeader;
    document.getElementById('myMessage').innerHTML = message;
    modal2.style.display = "block";
}    

/* SECTION - FULLSCREEN */

function launchIntoFullscreen(element) {
    if(element.requestFullscreen) {
        element.requestFullscreen();
    } else if(element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    } else if(element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    } else if(element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
}
  
function exitFullscreen() {
    if(document.exitFullscreen) {
        document.exitFullscreen();
    } else if(document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if(document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    }
}

function fullScreenSwitch() {
    if (fullScreen == 0) { 
        fullScreen = 1;  
        launchIntoFullscreen(document.documentElement);
    } else {
        fullScreen = 0;  
        exitFullscreen();
    }
}

/* Search */

function searchResourceModule(inputID, searchCommand, module) {
    var searchString = document.getElementById(inputID).value;
    if (searchString == "") {
        alert("Search input is empty!");
    } else {
        document.title = searchCommand+":::"+module+":::"+searchString;
    }
}

/* SECTION - COMMAND */

function focusCommandInput() {
    var el = document.getElementById("commandInput");
    el.value = "";
    el.focus();
}

function ubaCommandChanged(cmd) {
    if (cmd.startsWith("_cp")) {
        cmd = "_menu:::";
    }
    essential = (cmd.search(/^_menu:::|^_vnsc:::|^_vndc:::|^_book:::|^_promise:::|^_harmony:::|^_biblenote:::|^_setconfig:::|^_history|^_open:::|^_htmlimage:::|^_website:::|^_commentary:::|^_commentaries:::|^_chapters:::|^_verses:::|^_commentarychapters:::|^_commentaryverses:::|^_qr:::/i));
    const ignore = ["_stayOnSameTab:::"];
    if ((essential >= 0) || (!(cmd.startsWith("_")) && !(ignore.includes(cmd)))) {
        window.parent.submitCommand(cmd);
    } else if (!(ignore.includes(cmd))) {
        if (cmd.startsWith("_command:::")) {
            cmd = cmd.replace("_command:::", "");
        }
        displayCommand(cmd);
    }
}

function displayCommand(cmd) {
    el = window.parent.document.getElementById('commandInput');
    el.value = cmd;
    el.focus();
}

function submitCommand(cmd) {
    el = document.getElementById('commandInput');
    el.value = cmd;
    document.getElementById("commandForm").submit();
}

function submitTextCommand(id) {
    el = document.getElementById(id);
    submitCommand("BIBLE:::" + el.value + ":::");
}

function submitBookCommand(id) {
    el = document.getElementById(id);
    value = el.options[el.selectedIndex].text;
    submitCommand(value);
}

function submitVerseActionCommand(id) {
    el = document.getElementById(id);
    value = el.options[el.selectedIndex].value;
    submitCommand(value);
}

/* SECTION - INTERFACE */

function updateBook(bible, lang) {

    //modules using MarvelBible versification
    var MBversification = ['MOB','MAB','MPB','MTB','MIB'];
    //modules using KJV versification
    var KJVversification = ['KJV'];
    
    if (MBversification.indexOf(bible) >= 0) {
    
    // MarvelBible versification
    activeBCV = [
    [0], 
    [0, 31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26], 
    [0, 22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38], 
    [0, 17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34], 
    [0, 54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13], 
    [0, 46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12], 
    [0, 18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33], 
    [0, 36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25], 
    [0, 22, 23, 18, 22], 
    [0, 28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13], 
    [0, 27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25], 
    [0, 53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53], 
    [0, 18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30], 
    [0, 54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30], 
    [0, 17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23], 
    [0, 11, 70, 13, 24, 17, 22, 28, 36, 15, 44], 
    [0, 11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31], 
    [0, 22, 23, 15, 17, 14, 14, 10, 17, 32, 3], 
    [0, 22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17], 
    [0, 6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6], 
    [0, 33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31], 
    [0, 18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14], 
    [0, 17, 17, 11, 16, 16, 13, 13, 14], 
    [0, 31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24], 
    [0, 19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34], 
    [0, 22, 22, 66, 22, 22], 
    [0, 28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35], 
    [0, 21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13], 
    [0, 11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9], 
    [0, 20, 32, 21], 
    [0, 15, 16, 15, 13, 27, 14, 17, 14, 15], 
    [0, 21], 
    [0, 17, 10, 10, 11], 
    [0, 16, 13, 12, 13, 15, 16, 20], 
    [0, 15, 13, 19], 
    [0, 17, 20, 19], 
    [0, 18, 15, 20], 
    [0, 15, 23], 
    [0, 21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21], 
    [0, 14, 17, 18, 6], 
    [0, 25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20], 
    [0, 45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20], 
    [0, 80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53], 
    [0, 51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25], 
    [0, 26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 40, 38, 40, 30, 35, 27, 27, 32, 44, 31], 
    [0, 32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27], 
    [0, 31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24], 
    [0, 24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 13], 
    [0, 24, 21, 29, 31, 26, 18], 
    [0, 23, 22, 21, 32, 33, 24], 
    [0, 30, 30, 21, 23], 
    [0, 29, 23, 25, 18], 
    [0, 10, 20, 13, 18, 28], 
    [0, 12, 17, 18], 
    [0, 20, 15, 16, 16, 25, 21], 
    [0, 18, 26, 17, 22], 
    [0, 16, 15, 15], 
    [0, 25], 
    [0, 14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25], 
    [0, 27, 26, 18, 17, 20], 
    [0, 25, 25, 22, 19, 14], 
    [0, 21, 22, 18], 
    [0, 10, 29, 24, 21, 21], 
    [0, 13], 
    [0, 15], 
    [0, 25], 
    [0, 20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 18, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
    ];
    
    defaultBookMenu(lang);
    
    } else if ((KJVversification.indexOf(bible) >= 0) || (bible.lastIndexOf('c', 0) === 0)) {
    
    // KJV versification
    activeBCV = [
    [0], 
    [0, 31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26], 
    [0, 22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38], 
    [0, 17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34], 
    [0, 54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13], 
    [0, 46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12], 
    [0, 18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33], 
    [0, 36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25], 
    [0, 22, 23, 18, 22], 
    [0, 28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13], 
    [0, 27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25], 
    [0, 53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53], 
    [0, 18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30], 
    [0, 54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30], 
    [0, 17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23], 
    [0, 11, 70, 13, 24, 17, 22, 28, 36, 15, 44], 
    [0, 11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31], 
    [0, 22, 23, 15, 17, 14, 14, 10, 17, 32, 3], 
    [0, 22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17], 
    [0, 6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6], 
    [0, 33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31], 
    [0, 18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14], 
    [0, 17, 17, 11, 16, 16, 13, 13, 14], 
    [0, 31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24], 
    [0, 19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34], 
    [0, 22, 22, 66, 22, 22], 
    [0, 28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35], 
    [0, 21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13], 
    [0, 11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9], 
    [0, 20, 32, 21], 
    [0, 15, 16, 15, 13, 27, 14, 17, 14, 15], 
    [0, 21], 
    [0, 17, 10, 10, 11], 
    [0, 16, 13, 12, 13, 15, 16, 20], 
    [0, 15, 13, 19], 
    [0, 17, 20, 19], 
    [0, 18, 15, 20], 
    [0, 15, 23], 
    [0, 21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21], 
    [0, 14, 17, 18, 6], 
    [0, 25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20], 
    [0, 45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20], 
    [0, 80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53], 
    [0, 51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25], 
    [0, 26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31], 
    [0, 32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27], 
    [0, 31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24], 
    [0, 24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14], 
    [0, 24, 21, 29, 31, 26, 18], 
    [0, 23, 22, 21, 32, 33, 24], 
    [0, 30, 30, 21, 23], 
    [0, 29, 23, 25, 18], 
    [0, 10, 20, 13, 18, 28], 
    [0, 12, 17, 18], 
    [0, 20, 15, 16, 16, 25, 21], 
    [0, 18, 26, 17, 22], 
    [0, 16, 15, 15], 
    [0, 25], 
    [0, 14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25], 
    [0, 27, 26, 18, 17, 20], 
    [0, 25, 25, 22, 19, 14], 
    [0, 21, 22, 18], 
    [0, 10, 29, 24, 21, 21], 
    [0, 13], 
    [0, 14], 
    [0, 25], 
    [0, 20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
    ];
    
    defaultBookMenu(lang);
    
    } else {
    
    // clear master bcv and draw bcv from database later
    activeBCV = [1];
    document.getElementById('bookMenu').innerHTML = '<navItem><i>... loading ...</i></navItem>';
    showBooks(bible);
    
    }
    
    }
    
    function showBooks(bible) {
      var xhttp; 
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        document.getElementById("bookMenu").innerHTML = this.responseText;
        }
      };
      xhttp.open("GET", "getBCV.php?book="+bible, true);
      xhttp.send();
    }
    
function defaultBookMenu(lang) {
    
    if (lang == "traditional.html") {

        document.getElementById('bookMenu').innerHTML = '' +
        '<div class="bookSection">' +
        '<navitem onclick="navB(1,\'創世記\')">創世記</navitem><br>' +
        '<navitem onclick="navB(2,\'出埃及記\')">出埃及記</navitem><br>' +
        '<navitem onclick="navB(3,\'利未記\')">利未記</navitem><br>' +
        '<navitem onclick="navB(4,\'民數記\')">民數記</navitem><br>' +
        '<navitem onclick="navB(5,\'申命記\')">申命記</navitem><br>' +
        '<navitem onclick="navB(6,\'約書亞記\')">約書亞記</navitem><br>' +
        '<navitem onclick="navB(7,\'士師記\')">士師記</navitem><br>' +
        '<navitem onclick="navB(8,\'路得記\')">路得記</navitem><br>' +
        '<navitem onclick="navB(9,\'撒母耳記上\')">撒母耳記上</navitem><br>' +
        '<navitem onclick="navB(10,\'撒母耳記下\')">撒母耳記下</navitem><br>' +
        '<navitem onclick="navB(11,\'列王紀上\')">列王紀上</navitem><br>' +
        '<navitem onclick="navB(12,\'列王紀下\')">列王紀下</navitem><br>' +
        '<navitem onclick="navB(13,\'歷代志上\')">歷代志上</navitem><br>' +
        '<navitem onclick="navB(14,\'歷代志下\')">歷代志下</navitem><br>' +
        '<navitem onclick="navB(15,\'以斯拉記\')">以斯拉記</navitem><br>' +
        '<navitem onclick="navB(16,\'尼希米記\')">尼希米記</navitem><br>' +
        '<navitem onclick="navB(17,\'以斯帖記\')">以斯帖記</navitem><br>' +
        '<navitem onclick="navB(18,\'約伯記\')">約伯記</navitem><br>' +
        '<navitem onclick="navB(19,\'詩篇\')">詩篇</navitem><br>' +
        '<navitem onclick="navB(20,\'箴言\')">箴言</navitem><br>' +
        '<navitem onclick="navB(21,\'傳道書\')">傳道書</navitem><br>' +
        '<navitem onclick="navB(22,\'雅歌\')">雅歌</navitem><br>' +
        '<navitem onclick="navB(23,\'以賽亞書\')">以賽亞書</navitem><br>' +
        '<navitem onclick="navB(24,\'耶利米書\')">耶利米書</navitem><br>' +
        '<navitem onclick="navB(25,\'耶利米哀歌\')">耶利米哀歌</navitem><br>' +
        '<navitem onclick="navB(26,\'以西結書\')">以西結書</navitem><br>' +
        '<navitem onclick="navB(27,\'但以理書\')">但以理書</navitem><br>' +
        '<navitem onclick="navB(28,\'何西阿書\')">何西阿書</navitem><br>' +
        '<navitem onclick="navB(29,\'約珥書\')">約珥書</navitem><br>' +
        '<navitem onclick="navB(30,\'阿摩司書\')">阿摩司書</navitem><br>' +
        '<navitem onclick="navB(31,\'俄巴底亞書\')">俄巴底亞書</navitem><br>' +
        '<navitem onclick="navB(32,\'約拿書\')">約拿書</navitem><br>' +
        '<navitem onclick="navB(33,\'彌迦書\')">彌迦書</navitem><br>' +
        '<navitem onclick="navB(34,\'那鴻書\')">那鴻書</navitem><br>' +
        '<navitem onclick="navB(35,\'哈巴谷書\')">哈巴谷書</navitem><br>' +
        '<navitem onclick="navB(36,\'西番雅書\')">西番雅書</navitem><br>' +
        '<navitem onclick="navB(37,\'哈該書\')">哈該書</navitem><br>' +
        '<navitem onclick="navB(38,\'撒迦利亞書\')">撒迦利亞書</navitem><br>' +
        '<navitem onclick="navB(39,\'瑪拉基書\')">瑪拉基書</navitem><br>' +
        '</div>' +
        '<div class="bookSection">' +
        '<navitem onclick="navB(40,\'馬太福音\')">馬太福音</navitem><br>' +
        '<navitem onclick="navB(41,\'馬可福音\')">馬可福音</navitem><br>' +
        '<navitem onclick="navB(42,\'路加福音\')">路加福音</navitem><br>' +
        '<navitem onclick="navB(43,\'約翰福音\')">約翰福音</navitem><br>' +
        '<navitem onclick="navB(44,\'使徒行傳\')">使徒行傳</navitem><br>' +
        '<navitem onclick="navB(45,\'羅馬書\')">羅馬書</navitem><br>' +
        '<navitem onclick="navB(46,\'哥林多前書\')">哥林多前書</navitem><br>' +
        '<navitem onclick="navB(47,\'哥林多後書\')">哥林多後書</navitem><br>' +
        '<navitem onclick="navB(48,\'加拉太書\')">加拉太書</navitem><br>' +
        '<navitem onclick="navB(49,\'以弗所書\')">以弗所書</navitem><br>' +
        '<navitem onclick="navB(50,\'腓立比書\')">腓立比書</navitem><br>' +
        '<navitem onclick="navB(51,\'歌羅西書\')">歌羅西書</navitem><br>' +
        '<navitem onclick="navB(52,\'帖撒羅尼迦前書\')">帖撒羅尼迦前書</navitem><br>' +
        '<navitem onclick="navB(53,\'帖撒羅尼迦後書\')">帖撒羅尼迦後書</navitem><br>' +
        '<navitem onclick="navB(54,\'提摩太前書\')">提摩太前書</navitem><br>' +
        '<navitem onclick="navB(55,\'提摩太後書\')">提摩太後書</navitem><br>' +
        '<navitem onclick="navB(56,\'提多書\')">提多書</navitem><br>' +
        '<navitem onclick="navB(57,\'腓利門書\')">腓利門書</navitem><br>' +
        '<navitem onclick="navB(58,\'希伯來書\')">希伯來書</navitem><br>' +
        '<navitem onclick="navB(59,\'雅各書\')">雅各書</navitem><br>' +
        '<navitem onclick="navB(60,\'彼得前書\')">彼得前書</navitem><br>' +
        '<navitem onclick="navB(61,\'彼得後書\')">彼得後書</navitem><br>' +
        '<navitem onclick="navB(62,\'約翰一書\')">約翰一書</navitem><br>' +
        '<navitem onclick="navB(63,\'約翰二書\')">約翰二書</navitem><br>' +
        '<navitem onclick="navB(64,\'約翰三書\')">約翰三書</navitem><br>' +
        '<navitem onclick="navB(65,\'猶大書\')">猶大書</navitem><br>' +
        '<navitem onclick="navB(66,\'啟示錄\')">啟示錄</navitem><br>' +
        '</div>' +
        '';

    } else if (lang == "simplified.html") {

        document.getElementById('bookMenu').innerHTML = '' +
        '<div class="bookSection">' +
        '<navitem onclick="navB(1,\'创世记\')">创世记</navitem><br>' +
        '<navitem onclick="navB(2,\'出埃及记\')">出埃及记</navitem><br>' +
        '<navitem onclick="navB(3,\'利未记\')">利未记</navitem><br>' +
        '<navitem onclick="navB(4,\'民数记\')">民数记</navitem><br>' +
        '<navitem onclick="navB(5,\'申命记\')">申命记</navitem><br>' +
        '<navitem onclick="navB(6,\'约书亚记\')">约书亚记</navitem><br>' +
        '<navitem onclick="navB(7,\'士师记\')">士师记</navitem><br>' +
        '<navitem onclick="navB(8,\'路得记\')">路得记</navitem><br>' +
        '<navitem onclick="navB(9,\'撒母耳记上\')">撒母耳记上</navitem><br>' +
        '<navitem onclick="navB(10,\'撒母耳记下\')">撒母耳记下</navitem><br>' +
        '<navitem onclick="navB(11,\'列王纪上\')">列王纪上</navitem><br>' +
        '<navitem onclick="navB(12,\'列王纪下\')">列王纪下</navitem><br>' +
        '<navitem onclick="navB(13,\'历代志上\')">历代志上</navitem><br>' +
        '<navitem onclick="navB(14,\'历代志下\')">历代志下</navitem><br>' +
        '<navitem onclick="navB(15,\'以斯拉记\')">以斯拉记</navitem><br>' +
        '<navitem onclick="navB(16,\'尼希米记\')">尼希米记</navitem><br>' +
        '<navitem onclick="navB(17,\'以斯帖记\')">以斯帖记</navitem><br>' +
        '<navitem onclick="navB(18,\'约伯记\')">约伯记</navitem><br>' +
        '<navitem onclick="navB(19,\'诗篇\')">诗篇</navitem><br>' +
        '<navitem onclick="navB(20,\'箴言\')">箴言</navitem><br>' +
        '<navitem onclick="navB(21,\'传道书\')">传道书</navitem><br>' +
        '<navitem onclick="navB(22,\'雅歌\')">雅歌</navitem><br>' +
        '<navitem onclick="navB(23,\'以赛亚书\')">以赛亚书</navitem><br>' +
        '<navitem onclick="navB(24,\'耶利米书\')">耶利米书</navitem><br>' +
        '<navitem onclick="navB(25,\'耶利米哀歌\')">耶利米哀歌</navitem><br>' +
        '<navitem onclick="navB(26,\'以西结书\')">以西结书</navitem><br>' +
        '<navitem onclick="navB(27,\'但以理书\')">但以理书</navitem><br>' +
        '<navitem onclick="navB(28,\'何西阿书\')">何西阿书</navitem><br>' +
        '<navitem onclick="navB(29,\'约珥书\')">约珥书</navitem><br>' +
        '<navitem onclick="navB(30,\'阿摩司书\')">阿摩司书</navitem><br>' +
        '<navitem onclick="navB(31,\'俄巴底亚书\')">俄巴底亚书</navitem><br>' +
        '<navitem onclick="navB(32,\'约拿书\')">约拿书</navitem><br>' +
        '<navitem onclick="navB(33,\'弥迦书\')">弥迦书</navitem><br>' +
        '<navitem onclick="navB(34,\'那鸿书\')">那鸿书</navitem><br>' +
        '<navitem onclick="navB(35,\'哈巴谷书\')">哈巴谷书</navitem><br>' +
        '<navitem onclick="navB(36,\'西番雅书\')">西番雅书</navitem><br>' +
        '<navitem onclick="navB(37,\'哈该书\')">哈该书</navitem><br>' +
        '<navitem onclick="navB(38,\'撒迦利亚书\')">撒迦利亚书</navitem><br>' +
        '<navitem onclick="navB(39,\'玛拉基书\')">玛拉基书</navitem><br>' +
        '</div>' +
        '<div class="bookSection">' +
        '<navitem onclick="navB(40,\'马太福音\')">马太福音</navitem><br>' +
        '<navitem onclick="navB(41,\'马可福音\')">马可福音</navitem><br>' +
        '<navitem onclick="navB(42,\'路加福音\')">路加福音</navitem><br>' +
        '<navitem onclick="navB(43,\'约翰福音\')">约翰福音</navitem><br>' +
        '<navitem onclick="navB(44,\'使徒行传\')">使徒行传</navitem><br>' +
        '<navitem onclick="navB(45,\'罗马书\')">罗马书</navitem><br>' +
        '<navitem onclick="navB(46,\'哥林多前书\')">哥林多前书</navitem><br>' +
        '<navitem onclick="navB(47,\'哥林多后书\')">哥林多后书</navitem><br>' +
        '<navitem onclick="navB(48,\'加拉太书\')">加拉太书</navitem><br>' +
        '<navitem onclick="navB(49,\'以弗所书\')">以弗所书</navitem><br>' +
        '<navitem onclick="navB(50,\'腓立比书\')">腓立比书</navitem><br>' +
        '<navitem onclick="navB(51,\'歌罗西书\')">歌罗西书</navitem><br>' +
        '<navitem onclick="navB(52,\'帖撒罗尼迦前书\')">帖撒罗尼迦前书</navitem><br>' +
        '<navitem onclick="navB(53,\'帖撒罗尼迦后书\')">帖撒罗尼迦后书</navitem><br>' +
        '<navitem onclick="navB(54,\'提摩太前书\')">提摩太前书</navitem><br>' +
        '<navitem onclick="navB(55,\'提摩太后书\')">提摩太后书</navitem><br>' +
        '<navitem onclick="navB(56,\'提多书\')">提多书</navitem><br>' +
        '<navitem onclick="navB(57,\'腓利门书\')">腓利门书</navitem><br>' +
        '<navitem onclick="navB(58,\'希伯来书\')">希伯来书</navitem><br>' +
        '<navitem onclick="navB(59,\'雅各书\')">雅各书</navitem><br>' +
        '<navitem onclick="navB(60,\'彼得前书\')">彼得前书</navitem><br>' +
        '<navitem onclick="navB(61,\'彼得后书\')">彼得后书</navitem><br>' +
        '<navitem onclick="navB(62,\'约翰一书\')">约翰一书</navitem><br>' +
        '<navitem onclick="navB(63,\'约翰二书\')">约翰二书</navitem><br>' +
        '<navitem onclick="navB(64,\'约翰三书\')">约翰三书</navitem><br>' +
        '<navitem onclick="navB(65,\'犹大书\')">犹大书</navitem><br>' +
        '<navitem onclick="navB(66,\'启示录\')">启示录</navitem><br>' +
        '</div>' +
        '';

    } else {

        document.getElementById('bookMenu').innerHTML = '' +
        '<div class="bookSection">' +
        '<navitem onclick="navB(1,\'Genesis\')">Genesis</navitem><br>' +
        '<navitem onclick="navB(2,\'Exodus\')">Exodus</navitem><br>' +
        '<navitem onclick="navB(3,\'Leviticus\')">Leviticus</navitem><br>' +
        '<navitem onclick="navB(4,\'Numbers\')">Numbers</navitem><br>' +
        '<navitem onclick="navB(5,\'Deuteronomy\')">Deuteronomy</navitem><br>' +
        '<navitem onclick="navB(6,\'Joshua\')">Joshua</navitem><br>' +
        '<navitem onclick="navB(7,\'Judges\')">Judges</navitem><br>' +
        '<navitem onclick="navB(8,\'Ruth\')">Ruth</navitem><br>' +
        '<navitem onclick="navB(9,\'1 Samuel\')">1 Samuel</navitem><br>' +
        '<navitem onclick="navB(10,\'2 Samuel\')">2 Samuel</navitem><br>' +
        '<navitem onclick="navB(11,\'1 Kings\')">1 Kings</navitem><br>' +
        '<navitem onclick="navB(12,\'2 Kings\')">2 Kings</navitem><br>' +
        '<navitem onclick="navB(13,\'1 Chronicles\')">1 Chronicles</navitem><br>' +
        '<navitem onclick="navB(14,\'2 Chronicles\')">2 Chronicles</navitem><br>' +
        '<navitem onclick="navB(15,\'Ezra\')">Ezra</navitem><br>' +
        '<navitem onclick="navB(16,\'Nehemiah\')">Nehemiah</navitem><br>' +
        '<navitem onclick="navB(17,\'Esther\')">Esther</navitem><br>' +
        '<navitem onclick="navB(18,\'Job\')">Job</navitem><br>' +
        '<navitem onclick="navB(19,\'Psalm\')">Psalm</navitem><br>' +
        '<navitem onclick="navB(20,\'Proverbs\')">Proverbs</navitem><br>' +
        '<navitem onclick="navB(21,\'Ecclesiastes\')">Ecclesiastes</navitem><br>' +
        '<navitem onclick="navB(22,\'Song of Songs\')">Song of Songs</navitem><br>' +
        '<navitem onclick="navB(23,\'Isaiah\')">Isaiah</navitem><br>' +
        '<navitem onclick="navB(24,\'Jeremiah\')">Jeremiah</navitem><br>' +
        '<navitem onclick="navB(25,\'Lamentations\')">Lamentations</navitem><br>' +
        '<navitem onclick="navB(26,\'Ezekiel\')">Ezekiel</navitem><br>' +
        '<navitem onclick="navB(27,\'Daniel\')">Daniel</navitem><br>' +
        '<navitem onclick="navB(28,\'Hosea\')">Hosea</navitem><br>' +
        '<navitem onclick="navB(29,\'Joel\')">Joel</navitem><br>' +
        '<navitem onclick="navB(30,\'Amos\')">Amos</navitem><br>' +
        '<navitem onclick="navB(31,\'Obadiah\')">Obadiah</navitem><br>' +
        '<navitem onclick="navB(32,\'Jonah\')">Jonah</navitem><br>' +
        '<navitem onclick="navB(33,\'Micah\')">Micah</navitem><br>' +
        '<navitem onclick="navB(34,\'Nahum\')">Nahum</navitem><br>' +
        '<navitem onclick="navB(35,\'Habakkuk\')">Habakkuk</navitem><br>' +
        '<navitem onclick="navB(36,\'Zephaniah\')">Zephaniah</navitem><br>' +
        '<navitem onclick="navB(37,\'Haggai\')">Haggai</navitem><br>' +
        '<navitem onclick="navB(38,\'Zechariah\')">Zechariah</navitem><br>' +
        '<navitem onclick="navB(39,\'Malachi\')">Malachi</navitem><br>' +
        '</div>' +
        '<div class="bookSection">' +
        '<navitem onclick="navB(40,\'Matthew\')">Matthew</navitem><br>' +
        '<navitem onclick="navB(41,\'Mark\')">Mark</navitem><br>' +
        '<navitem onclick="navB(42,\'Luke\')">Luke</navitem><br>' +
        '<navitem onclick="navB(43,\'John\')">John</navitem><br>' +
        '<navitem onclick="navB(44,\'Acts\')">Acts</navitem><br>' +
        '<navitem onclick="navB(45,\'Romans\')">Romans</navitem><br>' +
        '<navitem onclick="navB(46,\'1 Corinthians\')">1 Corinthians</navitem><br>' +
        '<navitem onclick="navB(47,\'2 Corinthians\')">2 Corinthians</navitem><br>' +
        '<navitem onclick="navB(48,\'Galatians\')">Galatians</navitem><br>' +
        '<navitem onclick="navB(49,\'Ephesians\')">Ephesians</navitem><br>' +
        '<navitem onclick="navB(50,\'Philippians\')">Philippians</navitem><br>' +
        '<navitem onclick="navB(51,\'Colossians\')">Colossians</navitem><br>' +
        '<navitem onclick="navB(52,\'1 Thessalonians\')">1 Thessalonians</navitem><br>' +
        '<navitem onclick="navB(53,\'2 Thessalonians\')">2 Thessalonians</navitem><br>' +
        '<navitem onclick="navB(54,\'1 Timothy\')">1 Timothy</navitem><br>' +
        '<navitem onclick="navB(55,\'2 Timothy\')">2 Timothy</navitem><br>' +
        '<navitem onclick="navB(56,\'Titus\')">Titus</navitem><br>' +
        '<navitem onclick="navB(57,\'Philemon\')">Philemon</navitem><br>' +
        '<navitem onclick="navB(58,\'Hebrews\')">Hebrews</navitem><br>' +
        '<navitem onclick="navB(59,\'James\')">James</navitem><br>' +
        '<navitem onclick="navB(60,\'1 Peter\')">1 Peter</navitem><br>' +
        '<navitem onclick="navB(61,\'2 Peter\')">2 Peter</navitem><br>' +
        '<navitem onclick="navB(62,\'1 John\')">1 John</navitem><br>' +
        '<navitem onclick="navB(63,\'2 John\')">2 John</navitem><br>' +
        '<navitem onclick="navB(64,\'3 John\')">3 John</navitem><br>' +
        '<navitem onclick="navB(65,\'Jude\')">Jude</navitem><br>' +
        '<navitem onclick="navB(66,\'Revelation\')">Revelation</navitem><br>' +
        '</div>' +
        '';
    }

}
    
function updateChapter(book) {
    if (activeBCV[0] == 1) {
        document.getElementById("chapters").innerHTML = '<navItem><i>... loading ...</i></navItem>';
        if (changeVerse == 1) {
            showChapters(mod,book)
        } else if (changeVerse == 2) {
            showChapters(parallelVer,book)
        }
    } else {
        var chapters = '';
        var i;
        for (i = 1; i < (activeBCV[book].length); i++) { 
            chapters += '<navItem class="numPad" onclick="navC(' + i + ')">' + i + '</navItem>';   
        }
        document.getElementById("chapters").innerHTML = chapters;
    }
    
    }
    
    function showChapters(bible,book) {
      var xhttp; 
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        document.getElementById("chapters").innerHTML = this.responseText;
        }
      };
      xhttp.open("GET", "getBCV.php?chapter="+bible+"&b="+book, true);
      xhttp.send();
    }
    
    function showBookChapters(bible,book,chapter) {
      var xhttp; 
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        document.getElementById("chapters1").innerHTML = this.responseText;
        document.getElementById("chapters2").innerHTML = this.responseText;
        }
      };
      xhttp.open("GET", "getBCV.php?chapters="+bible+"&b="+book+"&c="+chapter, true);
      xhttp.send();
    }
    
    function updateVerse(book,chapter) {
    if (activeBCV[0] == 1) {
        document.getElementById("verses").innerHTML = '<navItem><i>... loading ...</i></navItem>';
        if (changeVerse == 1) {
            showVerses(mod,book,chapter)
        } else if (changeVerse == 2) {
            showVerses(parallelVer,book,chapter)
        }
    } else {
        var verses = '';
        var i;
        for (i = 1; i < (activeBCV[book][chapter] + 1); i++) { 
            verses += '<navItem class="numPad" onclick="navV(' + i + ')">' + i + '</navItem>';   
        }
        document.getElementById("verses").innerHTML = verses;
    }
    
    }
    
    function showVerses(bible,book,chapter) {
      var xhttp; 
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        document.getElementById("verses").innerHTML = this.responseText;
        }
      };
      xhttp.open("GET", "getBCV.php?verse="+bible+"&b="+book+"&c="+chapter, true);
      xhttp.send();
    }
    
    // START of OVERLAY-NAV
    
    function openNav(navID) {
        document.getElementById(navID).style.height = "100%";
    }
    
    function closeNav(navID) {
        document.getElementById(navID).style.height = "0%";
    }
    
    function navOT(ot,otDesc) {
    tempMod = ot;
    document.getElementById('modOT').innerHTML = otDesc;
    updateBook(ot);
    closeNav('navOT');
    }
    
    function navNT(nt,ntDesc) {
    tempMod = nt;
    document.getElementById('modNT').innerHTML = ntDesc;
    updateBook(nt);
    closeNav('navNT');
    }
    
    function navB(b,bDesc) {
    
    if (document.getElementById('id01').style.display == 'none') {
    currentB = b;
    currentBookName = bDesc;
    updateChapter(b);
    }
    else {
    tempB = b;
    document.getElementById('activeB').innerHTML = bDesc;
    checkONT(b);
    navC(1);
    navV(1);
    updateChapter(b);
    }
    closeNav('navB');
    openNav('navC');
    }
    
    function navC(c) {
    
    if (document.getElementById('id01').style.display == 'none') {
    currentC = c;
    updateVerse(currentB,currentC);
    }
    else {
    tempC = c;
    document.getElementById('activeC').innerHTML = c;
    navV(1);
    updateVerse(tempB,tempC);
    }
    closeNav('navC');
    openNav('navV');
    }
    
    function navV(v) {
    if (document.getElementById('id01').style.display == 'none') {
    currentV = v;
    closeNav('navV');
    submitCommand(currentBookName+" "+currentC+":"+currentV)
    }
    else {
    tempV = v;
    document.getElementById('activeV').innerHTML = v;
    closeNav('navV');
    }
    }
    /* END of OVERLAY-NAV */