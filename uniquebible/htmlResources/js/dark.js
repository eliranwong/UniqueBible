function hl1(id, cl, sn) {
    if (cl != '') {
        w3.addStyle('.c'+cl,'background-color','#4f4c4c');
    }
    if (sn != '') {
        w3.addStyle('.G'+sn,'background-color','#4f4c4c');
    }
    if (id != '') {
        var focalElement = document.getElementById('w'+id);
        if (focalElement != null) {
            document.getElementById('w'+id).style.background='#4f4c4c';
        }
    }
    if ((id != '') && (id.startsWith("l") != true)) {
        document.title = "_instantWord:::"+activeB+":::"+id;
    }
}
