function submitTextCommand(id) {
    el = document.getElementById(id);
    submitCommand("TEXT:::" + el.value);
}

function submitBookCommand(id) {
    el = document.getElementById(id);
    value = el.options[el.selectedIndex].text;
    submitCommand(value);
}

function submitCommand(cmd) {
    el = document.getElementById('commandInput');
    el.value = cmd;
    document.getElementById("commandForm").submit();
}
