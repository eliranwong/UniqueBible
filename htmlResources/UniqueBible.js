function bcvToVerseRefence(b,c,v) {
    var SBLabb = ["", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalm", "Proverbs", "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"];
    var abb = SBLabb[b];
    return abb+" "+c+":"+v;
}

function mbbcvToVerseRefence(b,c,v) {
    var MBBkList = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 190, 220, 230, 240, 250, 260, 290, 300, 310, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710, 720, 730];
    var b2 = MBBkList.indexOf(b);
    var SBLabb = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalm", "Proverbs", "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"];
    var abb = SBLabb[b2];
    return abb+" "+c+":"+v;
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
    document.title = "_INSTANT:::"+activeB+":::"+id;
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

function luV(v) {
    var verseReference = bcvToVerseRefence(activeB,activeC,v);
    document.title = "BIBLE:::"+activeText+":::"+verseReference;
}

function luW(v,wid,cl,lex,morph,bdb) {
    
}
