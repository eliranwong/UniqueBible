/* Onload functions */

function onBodyLoad() {
    cmd = decodeURIComponent(location.search);
    cmd = cmd.replace("?cmd=", "")
             .replace("+", " ");
    el = document.getElementById('commandInput')
    el.value = cmd
    el.focus();
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
  
  if (getMobileOperatingSystem() == 'iOS') {
      if (window.navigator.standalone) {
      messageUser('<h3>Exit Fullscreen in iOS/iPad/iPhone</h3>', '<p>To enter non-fullscreen mode in iOS/iPad/iPhone, use web browser (e.g. mobile Sarfari), instead home screen bookmark.</p>');
      }
      else {
      messageUser('<h3>Enter Fullscreen in iOS/iPad/iPhone</h3>', '<p>To enter fullscreen mode in iOS/iPad/iPhone, use a home screen bookmark directly.</p><p>How to save a home screen bookmark?<br>1) Open http://localhost:8080 with mobile Sarfari first.<br>2) Choose "Add to Home Screen" in action menu to save a bookmark.</p>');
      }
  }
  else {
      if (fullScreen == 0) { 
      fullScreen = 1;  
      launchIntoFullscreen(document.documentElement);
      }
      else {
      fullScreen = 0;  
      exitFullscreen();
      }
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

function ubaCommandChanged(cmd) {
    if (cmd.startsWith("_cp")) {
        cmd = "_menu:::";
    }
    essential = (cmd.search(/^_menu:::|^_vnsc:::|^_vndc:::|^_book:::|^_promise:::|^_history|^_open:::|^_htmlimage:::|^_website:::|^_commentary:::/i));
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
    submitCommand("TEXT:::" + el.value);
}

function submitBookCommand(id) {
    el = document.getElementById(id);
    value = el.options[el.selectedIndex].text;
    submitCommand(value);
}
