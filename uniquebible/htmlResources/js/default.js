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
    if ((id != '') && (id.startsWith("l") != true)) {
        document.title = "_instantWord:::"+activeB+":::"+id;
    }
}
