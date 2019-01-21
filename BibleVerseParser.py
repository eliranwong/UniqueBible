"""
Previously uploaded at https://github.com/eliranwong/bible-verse-parser
Modified for integration into theText.app

A python parser to parse bible verse references from a text.

This was originally created to tag resources for building <a href="https://marvel.bible">https://marvel.bible</a>.<br>
The script is now modified for general use.

Features:
1. Search for verse references from text file(s)
2. Add taggings on verse references
3. Support books of bible canon and apocrypha
4. Support tagging on chains of refernces, e.g. Rom 1:2, 3, 5, 8; 9:2, 10
5. Support books of one chapter only, like Obadiah 2, Jude 3, 3John 4, etc.
6. Support chapter references [references without verse number specified], e.g. Gen 1, 3-4; 8, 9-10.
7. Support standardisation of book abbreviations and verse reference format.
8. Support parsing multiple files in one go.

Usage:
Command line: python bible-verse-parser.py

User Interaction:
Prompting question (1) "Enter a file / folder name here: "<br>
Enter the name of a file, which you want to parse.
OR
Enter the name of a directory containing files, which you want you parse.

Prompting question (2) "Do you want to standardise the format of all bible verse references? [YES/NO] "<br>
Enter YES if you want to standardise all verse references with SBL-style-abbreviations and common format like Gen 2:4; Deut 6:4, etc.<br>
Any answers other than "YES" [case-insensitive] skip the standarisation.
"""

# import modules, which are ESSENTIAL for running BibleVerseParser
import re, glob, os
from ast import literal_eval

"""
START - class BibleVerseParser
"""

class BibleVerseParser:

    # variable to capture user preference on standardisation
    standardisation = ""

    # set a simple indicator
    workingIndicator = 0

    # SBL-style abbreviations
    standardAbbreviation = {
        "1": "Gen",
        "2": "Exod",
        "3": "Lev",
        "4": "Num",
        "5": "Deut",
        "6": "Josh",
        "7": "Judg",
        "8": "Ruth",
        "9": "1Sam",
        "10": "2Sam",
        "11": "1Kgs",
        "12": "2Kgs",
        "13": "1Chr",
        "14": "2Chr",
        "15": "Ezra",
        "16": "Neh",
        "17": "Esth",
        "18": "Job",
        "19": "Ps",
        "20": "Prov",
        "21": "Eccl",
        "22": "Song",
        "23": "Isa",
        "24": "Jer",
        "25": "Lam",
        "26": "Ezek",
        "27": "Dan",
        "28": "Hos",
        "29": "Joel",
        "30": "Amos",
        "31": "Obad",
        "32": "Jonah",
        "33": "Mic",
        "34": "Nah",
        "35": "Hab",
        "36": "Zeph",
        "37": "Hag",
        "38": "Zech",
        "39": "Mal",
        "40": "Matt",
        "41": "Mark",
        "42": "Luke",
        "43": "John",
        "44": "Acts",
        "45": "Rom",
        "46": "1Cor",
        "47": "2Cor",
        "48": "Gal",
        "49": "Eph",
        "50": "Phil",
        "51": "Col",
        "52": "1Thess",
        "53": "2Thess",
        "54": "1Tim",
        "55": "2Tim",
        "56": "Titus",
        "57": "Phlm",
        "58": "Heb",
        "59": "Jas",
        "60": "1Pet",
        "61": "2Pet",
        "62": "1John",
        "63": "2John",
        "64": "3John",
        "65": "Jude",
        "66": "Rev",
        "70": "Bar",
        "71": "AddDan",
        "72": "PrAzar",
        "73": "Bel",
        "75": "Sus",
        "76": "1Esd",
        "77": "2Esd",
        "78": "AddEsth",
        "79": "EpJer",
        "80": "Jdt",
        "81": "1Macc",
        "82": "2Macc",
        "83": "3Macc",
        "84": "4Macc",
        "85": "PrMan",
        "86": "Ps151",
        "87": "Sir",
        "88": "Tob",
        "89": "Wis",
        "90": "PssSol",
        "91": "Odes",
        "92": "EpLao",
    }

    # mapping bible book abbreviation / bible book name to book number
    marvelBibleBookNo = {
        "Ge.": "1",
        "Gen.": "1",
        "GEN.": "1",
        "Genesis": "1",
        "Gn.": "1",
        "Ex.": "2",
        "Exo.": "2",
        "EXO.": "2",
        "Exod.": "2",
        "Exodus": "2",
        "Le.": "3",
        "Lev.": "3",
        "LEV.": "3",
        "Leviticus": "3",
        "Lv.": "3",
        "Nb.": "4",
        "Nm.": "4",
        "Nu.": "4",
        "Num.": "4",
        "NUM.": "4",
        "Numbers": "4",
        "De.": "5",
        "Deu.": "5",
        "DEU.": "5",
        "Deut.": "5",
        "Deuteronomy": "5",
        "Dt.": "5",
        "Jos.": "6",
        "JOS.": "6",
        "Josh.": "6",
        "JoshA.": "6",
        "Joshua": "6",
        "Jsa.": "6",
        "JSA.": "6",
        "Jsh.": "6",
        "Jdb.": "7",
        "JDB.": "7",
        "Jdg.": "7",
        "JDG.": "7",
        "Jdgs.": "7",
        "Jg.": "7",
        "Judg.": "7",
        "JudgB.": "7",
        "Judges": "7",
        "Rth.": "8",
        "Ru.": "8",
        "Rut.": "8",
        "RUT.": "8",
        "Ruth": "8",
        "1 S.": "9",
        "1 Sa.": "9",
        "1 Sam.": "9",
        "1 Samuel": "9",
        "1 Sm.": "9",
        "1S.": "9",
        "1Sa.": "9",
        "1SA.": "9",
        "1Sam.": "9",
        "1st Sam.": "9",
        "1st Samuel": "9",
        "First Sam.": "9",
        "First Samuel": "9",
        "I Sa.": "9",
        "I Sam.": "9",
        "2 S.": "10",
        "2 Sa.": "10",
        "2 Sam.": "10",
        "2 Samuel": "10",
        "2 Sm.": "10",
        "2nd Sam.": "10",
        "2nd Samuel": "10",
        "2S.": "10",
        "2Sa.": "10",
        "2SA.": "10",
        "2Sam.": "10",
        "II Sa.": "10",
        "II Sam.": "10",
        "Second Sam.": "10",
        "Second Samuel": "10",
        "1 Kgs.": "11",
        "1 Ki.": "11",
        "1 Kings": "11",
        "1K.": "11",
        "1Kgs.": "11",
        "1Ki.": "11",
        "1KI.": "11",
        "1Kin.": "11",
        "1st Kgs.": "11",
        "1st Kings": "11",
        "First Kgs.": "11",
        "First Kings": "11",
        "I Kgs.": "11",
        "I Ki.": "11",
        "2 Kgs.": "12",
        "2 Ki.": "12",
        "2 Kings": "12",
        "2K.": "12",
        "2Kgs.": "12",
        "2Ki.": "12",
        "2KI.": "12",
        "2Kin.": "12",
        "2nd Kgs.": "12",
        "2nd Kings": "12",
        "II Kgs.": "12",
        "II Ki.": "12",
        "Second Kgs.": "12",
        "Second Kings": "12",
        "1 Ch.": "13",
        "1 Chr.": "13",
        "1 Chron.": "13",
        "1 Chronicles": "13",
        "1Ch.": "13",
        "1CH.": "13",
        "1Chr.": "13",
        "1Chron.": "13",
        "1st Chron.": "13",
        "1st Chronicles": "13",
        "First Chron.": "13",
        "First Chronicles": "13",
        "I Ch.": "13",
        "I Chr.": "13",
        "I Chron.": "13",
        "2 Ch.": "14",
        "2 Chr.": "14",
        "2 Chron.": "14",
        "2 Chronicles": "14",
        "2Ch.": "14",
        "2CH.": "14",
        "2Chr.": "14",
        "2Chron.": "14",
        "2nd Chron.": "14",
        "2nd Chronicles": "14",
        "II Ch.": "14",
        "II Chr.": "14",
        "II Chron.": "14",
        "Second Chron.": "14",
        "Second Chronicles": "14",
        "Ez.": "15",
        "Ezr.": "15",
        "EZR.": "15",
        "Ezra": "15",
        "Ne.": "16",
        "Neh.": "16",
        "NEH.": "16",
        "Nehemiah": "16",
        "Es.": "17",
        "Est.": "17",
        "EST.": "17",
        "Esth.": "17",
        "Esther": "17",
        "Jb.": "18",
        "Job": "18",
        "JOB": "18",
        "Ps.": "19",
        "Psa.": "19",
        "PSA.": "19",
        "Psalm": "19",
        "Psalms": "19",
        "Pslm.": "19",
        "Psm.": "19",
        "Pr.": "20",
        "Pro.": "20",
        "PRO.": "20",
        "Prov.": "20",
        "Proverbs": "20",
        "Prv.": "20",
        "Ec.": "21",
        "Ecc.": "21",
        "ECC.": "21",
        "Eccl.": "21",
        "Eccle.": "21",
        "Eccles.": "21",
        "Ecclesiastes": "21",
        "Qoh.": "21",
        "Cant.": "22",
        "Canticle of Canticles": "22",
        "Canticles": "22",
        "Sng.": "22",
        "SNG.": "22",
        "So.": "22",
        "Son.": "22",
        "Song": "22",
        "Song of Solomon": "22",
        "Song of Songs": "22",
        "SOS.": "22",
        "Is.": "23",
        "Isa.": "23",
        "ISA.": "23",
        "Isaiah": "23",
        "Je.": "24",
        "Jer.": "24",
        "JER.": "24",
        "Jeremiah": "24",
        "Jr.": "24",
        "La.": "25",
        "Lam.": "25",
        "LAM.": "25",
        "Lamentations": "25",
        "Eze.": "26",
        "Ezek.": "26",
        "Ezekiel": "26",
        "Ezk.": "26",
        "EZK.": "26",
        "Da.": "27",
        "Dan.": "27",
        "DAN.": "27",
        "Daniel": "27",
        "Dn.": "27",
        "Ho.": "28",
        "Hos.": "28",
        "HOS.": "28",
        "Hosea": "28",
        "Jl.": "29",
        "Joe.": "29",
        "Joel": "29",
        "Jol.": "29",
        "JOL.": "29",
        "Am.": "30",
        "Amo.": "30",
        "AMO.": "30",
        "Amos": "30",
        "Ob.": "31",
        "Oba.": "31",
        "OBA.": "31",
        "Obad.": "31",
        "Obadiah": "31",
        "Jnh.": "32",
        "Jon.": "32",
        "JON.": "32",
        "Jonah": "32",
        "Mc.": "33",
        "Mic.": "33",
        "MIC.": "33",
        "Micah": "33",
        "Na.": "34",
        "Nah.": "34",
        "Nahum": "34",
        "Nam.": "34",
        "NAM.": "34",
        "Hab.": "35",
        "HAB.": "35",
        "Habakkuk": "35",
        "Hb.": "35",
        "Zep.": "36",
        "ZEP.": "36",
        "Zeph.": "36",
        "Zephaniah": "36",
        "Zp.": "36",
        "Hag.": "37",
        "HAG.": "37",
        "Haggai": "37",
        "Hg.": "37",
        "Zc.": "38",
        "Zec.": "38",
        "ZEC.": "38",
        "Zech.": "38",
        "Zechariah": "38",
        "Mal.": "39",
        "MAL.": "39",
        "Malachi": "39",
        "Ml.": "39",
        "Mat.": "40",
        "MAT.": "40",
        "Matt.": "40",
        "Matthew": "40",
        "Mt.": "40",
        "Mar.": "41",
        "Mark": "41",
        "Mk.": "41",
        "Mr.": "41",
        "Mrk.": "41",
        "MRK.": "41",
        "Lk.": "42",
        "Luk.": "42",
        "LUK.": "42",
        "Luke": "42",
        "Jhn.": "43",
        "JHN.": "43",
        "Jn.": "43",
        "Joh.": "43",
        "John": "43",
        "Ac.": "44",
        "Act.": "44",
        "ACT.": "44",
        "Acts": "44",
        "Rm.": "45",
        "Ro.": "45",
        "Rom.": "45",
        "ROM.": "45",
        "Romans": "45",
        "1 Co.": "46",
        "1 Cor.": "46",
        "1 Corinthians": "46",
        "1Co.": "46",
        "1CO.": "46",
        "1Cor.": "46",
        "1Corinthians": "46",
        "1st Corinthians": "46",
        "First Corinthians": "46",
        "I Co.": "46",
        "I Cor.": "46",
        "I Corinthians": "46",
        "2 Co.": "47",
        "2 Cor.": "47",
        "2 Corinthians": "47",
        "2Co.": "47",
        "2CO.": "47",
        "2Cor.": "47",
        "2Corinthians": "47",
        "2nd Corinthians": "47",
        "II Co.": "47",
        "II Cor.": "47",
        "II Corinthians": "47",
        "Second Corinthians": "47",
        "Ga.": "48",
        "Gal.": "48",
        "GAL.": "48",
        "Galatians": "48",
        "Eph.": "49",
        "EPH.": "49",
        "Ephes.": "49",
        "Ephesians": "49",
        "Phi.": "50",
        "Phil.": "50",
        "Philip.": "50",
        "Philippians": "50",
        "Php.": "50",
        "PHP.": "50",
        "Pp.": "50",
        "Co.": "51",
        "Col.": "51",
        "COL.": "51",
        "Colossians": "51",
        "1 Th.": "52",
        "1 Thes.": "52",
        "1 Thess.": "52",
        "1 Thessalonians": "52",
        "1st Thess.": "52",
        "1st Thessalonians": "52",
        "1Th.": "52",
        "1TH.": "52",
        "1Thes.": "52",
        "1Thess.": "52",
        "1Thessalonians": "52",
        "First Thess.": "52",
        "First Thessalonians": "52",
        "I Th.": "52",
        "I Thes.": "52",
        "I Thess.": "52",
        "I Thessalonians": "52",
        "2 Th.": "53",
        "2 Thes.": "53",
        "2 Thess.": "53",
        "2 Thessalonians": "53",
        "2nd Thess.": "53",
        "2nd Thessalonians": "53",
        "2Th.": "53",
        "2TH.": "53",
        "2Thes.": "53",
        "2Thess.": "53",
        "2Thessalonians": "53",
        "II Th.": "53",
        "II Thes.": "53",
        "II Thess.": "53",
        "II Thessalonians": "53",
        "Second Thess.": "53",
        "Second Thessalonians": "53",
        "1 Ti.": "54",
        "1 Tim.": "54",
        "1 Timothy": "54",
        "1st Tim.": "54",
        "1st Timothy": "54",
        "1Ti.": "54",
        "1TI.": "54",
        "1Tim.": "54",
        "1Timothy": "54",
        "First Tim.": "54",
        "First Timothy": "54",
        "I Ti.": "54",
        "I Tim.": "54",
        "I Timothy": "54",
        "2 Ti.": "55",
        "2 Tim.": "55",
        "2 Timothy": "55",
        "2nd Tim.": "55",
        "2nd Timothy": "55",
        "2Ti.": "55",
        "2TI.": "55",
        "2Tim.": "55",
        "2Timothy": "55",
        "II Ti.": "55",
        "II Tim.": "55",
        "II Timothy": "55",
        "Second Tim.": "55",
        "Second Timothy": "55",
        "ti.": "56",
        "Tit.": "56",
        "TIT.": "56",
        "Titus": "56",
        "Philem.": "57",
        "Philemon": "57",
        "Phlm.": "57",
        "Phm.": "57",
        "PHM.": "57",
        "Pm.": "57",
        "Heb.": "58",
        "HEB.": "58",
        "Hebrews": "58",
        "Jam.": "59",
        "James": "59",
        "Jas.": "59",
        "JAS.": "59",
        "Jm.": "59",
        "Js.": "59",
        "1 P.": "60",
        "1 Pe.": "60",
        "1 Pet.": "60",
        "1 Peter": "60",
        "1 Pt.": "60",
        "1P.": "60",
        "1Pe.": "60",
        "1PE.": "60",
        "1Pet.": "60",
        "1Peter": "60",
        "1Pt.": "60",
        "1st Peter": "60",
        "First Peter": "60",
        "I Pe.": "60",
        "I Pet.": "60",
        "I Peter": "60",
        "I Pt.": "60",
        "2 P.": "61",
        "2 Pe.": "61",
        "2 Pet.": "61",
        "2 Peter": "61",
        "2 Pt.": "61",
        "2nd Peter": "61",
        "2P.": "61",
        "2Pe.": "61",
        "2PE.": "61",
        "2Pet.": "61",
        "2Peter": "61",
        "2Pt.": "61",
        "II Pe.": "61",
        "II Pet.": "61",
        "II Peter": "61",
        "II Pt.": "61",
        "Second Peter": "61",
        "1 J.": "62",
        "1 Jhn.": "62",
        "1 Jn.": "62",
        "1 John": "62",
        "1J.": "62",
        "1Jhn.": "62",
        "1Jn.": "62",
        "1JN.": "62",
        "1Jo.": "62",
        "1Joh.": "62",
        "1John": "62",
        "1st John": "62",
        "First John": "62",
        "I Jhn.": "62",
        "I Jn.": "62",
        "I Jo.": "62",
        "I Joh.": "62",
        "I John": "62",
        "2 J.": "63",
        "2 Jhn.": "63",
        "2 Jn.": "63",
        "2 John": "63",
        "2J.": "63",
        "2Jhn.": "63",
        "2Jn.": "63",
        "2JN.": "63",
        "2Jo.": "63",
        "2Joh.": "63",
        "2John": "63",
        "2nd John": "63",
        "II Jhn.": "63",
        "II Jn.": "63",
        "II Jo.": "63",
        "II Joh.": "63",
        "II John": "63",
        "Second John": "63",
        "3 J.": "64",
        "3 Jhn.": "64",
        "3 Jn.": "64",
        "3 John": "64",
        "3J.": "64",
        "3Jhn.": "64",
        "3Jn.": "64",
        "3JN.": "64",
        "3Jo.": "64",
        "3Joh.": "64",
        "3John": "64",
        "3rd John": "64",
        "III Jhn.": "64",
        "III Jn.": "64",
        "III Jo.": "64",
        "III Joh.": "64",
        "III John": "64",
        "Third John": "64",
        "Jd.": "65",
        "Jud.": "65",
        "JUD.": "65",
        "Jude": "65",
        "Apocalypse of John": "66",
        "Re.": "66",
        "Rev.": "66",
        "REV.": "66",
        "Revelation": "66",
        "Revelation to John": "66",
        "Rv.": "66",
        "The Revelation": "66",
        "Bar.": "70",
        "BAR.": "70",
        "Baruch": "70",
        "Add. Dan.": "71",
        "Adddan.": "71",
        "AddDan.": "71",
        "Additions to Daniel": "71",
        "Dag.": "71",
        "DAG.": "71",
        "DanGr.": "71",
        "DanTh.": "71",
        "Dnt.": "71",
        "DNT.": "71",
        "Azariah": "72",
        "Pr. Az.": "72",
        "Pr. Azar.": "72",
        "Prayer of Azariah": "72",
        "PrAzar.": "72",
        "S3Y.": "72",
        "Sg. of 3 Childr.": "72",
        "Sg. Three": "72",
        "Song of the Three Holy Children": "72",
        "Song of Thr.": "72",
        "Song of Three": "72",
        "Song of Three Children": "72",
        "Song of Three Jews": "72",
        "Song of Three Youths": "72",
        "Song Thr.": "72",
        "The Song of the Three Holy Children": "72",
        "The Song of Three Jews": "72",
        "The Song of Three Youths": "72",
        "Bel": "73",
        "BEL": "73",
        "Bel and Dr.": "73",
        "Bel and the Dragon": "73",
        "Bel.": "73",
        "BelTh.": "73",
        "Blt.": "73",
        "BLT.": "73",
        "Sst.": "75",
        "SST.": "75",
        "Sus.": "75",
        "SUS.": "75",
        "Susanna": "75",
        "SusTh.": "75",
        "1 Esd.": "76",
        "1 Esdr.": "76",
        "1 Esdras": "76",
        "1Es.": "76",
        "1ES.": "76",
        "1Esd.": "76",
        "1Esdr.": "76",
        "1Esdras.": "76",
        "1st Esdras": "76",
        "First Esdras": "76",
        "I Es.": "76",
        "I Esd.": "76",
        "I Esdr.": "76",
        "I Esdras": "76",
        "2 Esd.": "77",
        "2 Esdr.": "77",
        "2 Esdras": "77",
        "2Es.": "77",
        "2ES.": "77",
        "2Esd.": "77",
        "2Esdr.": "77",
        "2Esdras": "77",
        "2nd Esdras": "77",
        "II Es.": "77",
        "II Esd.": "77",
        "II Esdr.": "77",
        "II Esdras": "77",
        "Second Esdras": "77",
        "Add. Es.": "78",
        "Add. Esth.": "78",
        "AddEsth.": "78",
        "Additions to Esther": "78",
        "Ade.": "78",
        "ADE.": "78",
        "AEs.": "78",
        "Esg.": "78",
        "ESG.": "78",
        "EsthGr.": "78",
        "Rest of Esther": "78",
        "The Rest of Esther": "78",
        "Ep. Jer.": "79",
        "EpJer.": "79",
        "Let. Jer.": "79",
        "Letter of Jeremiah": "79",
        "Lje.": "79",
        "LJe.": "79",
        "LJE.": "79",
        "Ltr. Jer.": "79",
        "Jdt.": "80",
        "JDT.": "80",
        "Jdth.": "80",
        "Jth.": "80",
        "Judith": "80",
        "1 Mac.": "81",
        "1 Macc.": "81",
        "1 Maccabees": "81",
        "1M.": "81",
        "1Ma.": "81",
        "1MA.": "81",
        "1Mac.": "81",
        "1Macc.": "81",
        "1Maccabees": "81",
        "1st Maccabees": "81",
        "First Maccabees": "81",
        "I Ma.": "81",
        "I Mac.": "81",
        "I Macc.": "81",
        "I Maccabees": "81",
        "2 Mac.": "82",
        "2 Macc.": "82",
        "2 Maccabees": "82",
        "2M.": "82",
        "2Ma.": "82",
        "2MA.": "82",
        "2Mac.": "82",
        "2Macc.": "82",
        "2Maccabees": "82",
        "2nd Maccabees": "82",
        "II Ma.": "82",
        "II Mac.": "82",
        "II Macc.": "82",
        "II Maccabees": "82",
        "Second Maccabees": "82",
        "3 Mac.": "83",
        "3 Macc.": "83",
        "3 Maccabees": "83",
        "3M.": "83",
        "3Ma.": "83",
        "3MA.": "83",
        "3Mac.": "83",
        "3Macc.": "83",
        "3Maccabees": "83",
        "3rd Maccabees": "83",
        "III Ma.": "83",
        "III Mac.": "83",
        "III Macc.": "83",
        "III Maccabees": "83",
        "Third Maccabees": "83",
        "4 Mac.": "84",
        "4 Macc.": "84",
        "4 Maccabees": "84",
        "4M.": "84",
        "4Ma.": "84",
        "4MA.": "84",
        "4Mac.": "84",
        "4Macc.": "84",
        "4Maccabees": "84",
        "4th Maccabees": "84",
        "Fourth Maccabees": "84",
        "IV Ma.": "84",
        "IV Mac.": "84",
        "IV Macc.": "84",
        "IV Maccabees": "84",
        "Man.": "85",
        "MAN.": "85",
        "PMa.": "85",
        "Pr. Man": "85",
        "Pr. of Man.": "85",
        "Prayer of Manasseh": "85",
        "Prayer of Manasses": "85",
        "PrMan.": "85",
        "Add. Ps.": "86",
        "Add. Psalm": "86",
        "Additional Psalm": "86",
        "AddPs.": "86",
        "Ps. 151": "86",
        "Ps2.": "86",
        "PS2.": "86",
        "Ps151": "86",
        "Psalm 151": "86",
        "Ecclesiasticus": "87",
        "Ecclus.": "87",
        "Sir.": "87",
        "SIR.": "87",
        "Sirach": "87",
        "Sirp.": "87",
        "SirP.": "87",
        "Tb.": "88",
        "Tbs.": "88",
        "TBS.": "88",
        "TOB": "88",
        "Tob.": "88",
        "Tobit": "88",
        "TobS.": "88",
        "Wis.": "89",
        "WIS.": "89",
        "Wisd. of Sol.": "89",
        "Wisdom": "89",
        "Wisdom of Solomon": "89",
        "Ws.": "89",
        "Ps. Sol.": "90",
        "Ps. Solomon": "90",
        "Psalms of Solomon": "90",
        "Psalms Solomon": "90",
        "Pss.": "90",
        "PSS.": "90",
        "PsSol.": "90",
        "PssSol.": "90",
        "Oda.": "91",
        "ODA.": "91",
        "Ode.": "91",
        "Odes": "91",
        "Ep. Lao.": "92",
        "Ep. Laod.": "92",
        "Epist. Laodiceans": "92",
        "Epistle Laodiceans": "92",
        "Epistle to Laodiceans": "92",
        "Epistle to the Laodiceans": "92",
        "EpLao.": "92",
        "Lao.": "92",
        "Laod.": "92",
        "Laodiceans": "92",
    }

    # initialisation
    def __init__(self, standardisation):
        # set preference of standardisation
        self.standardisation = standardisation

        # sort dictionary by alphabet of keys
        marvelBibleBookNoTemp = {}
        for book in sorted(self.marvelBibleBookNo.keys()) :
            marvelBibleBookNoTemp[book] = self.marvelBibleBookNo[book]

        # sort dictionary by length of keys
        self.marvelBibleBookNo = {}
        for book in sorted(marvelBibleBookNoTemp, key=len, reverse=True):
            self.marvelBibleBookNo[book] = marvelBibleBookNoTemp[book]

    # function for indicating working status
    def updateWorkingIndicator(self):
        runningIndication = ["／", "－", "＼", "｜"]
        print("... parsing ... "+runningIndication[self.workingIndicator])
        if self.workingIndicator == 3:
            self.workingIndicator = 0
        else:
            self.workingIndicator += 1

    # function for converting b c v integers to verse reference string
    def bcvToVerseReference(self, b, c, v):
        abbreviation = self.standardAbbreviation[str(b)]
        chapter = str(c)
        verse = str(v)
        return abbreviation+" "+chapter+":"+verse

    # function for standardising all verse references in a block of text; use standard set of abbreviations defined below; format references as <abbreviation> <chapter>:<verse>
    def standardReference(self, text):
        standardisedText = text

        #self.updateWorkingIndicator()

        for booknumber in self.standardAbbreviation:
            #self.updateWorkingIndicator()
            abbreviation = self.standardAbbreviation[booknumber]
            standardisedText = re.sub('<ref onclick="bcv\('+booknumber+',([0-9]+?),([0-9]+?)\)">.*?</ref>', '<ref onclick="bcv('+booknumber+r',\1,\2)">'+abbreviation+r' \1:\2</ref>', standardisedText)
        return standardisedText

    def parseText(self, text):
        # add a space at the end of the text, to avoid indefinite loop in later steps
        #this extra space will be removed when parsing is finished.
        taggedText = text+" "
        
        # remove bcv tags, if any, to avoid duplication of tagging in later steps
        p = re.compile('<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9]+?\)">')
        if p.search(taggedText):
            taggedText = re.sub('<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9]+?\)">(.*?)</ref>', r'\1', taggedText, flags=re.M)

        # search for books; mark them with book numbers, used by https://marvel.bible
        for book in self.marvelBibleBookNo:
            #self.updateWorkingIndicator()
            # get the string of book name
            bookString = book
            # make dot "." optional for an abbreviation
            bookString = re.sub('\.', r'[\.]*?', bookString, flags=re.M)
            # make space " " optional in some cases
            bookString = re.sub('^([0-9]+?) ', r'\1[ ]*?', bookString, flags=re.M)
            bookString = re.sub('^([I]+?) ', r'\1[ ]*?', bookString, flags=re.M)
            bookString = re.sub('^(IV) ', r'\1[ ]*?', bookString, flags=re.M)
            # get assigned book number from dictionary
            booknumber = self.marvelBibleBookNo[book]
            # search & replace for marking book
            taggedText = re.sub('('+bookString+') ([0-9])', '『'+booknumber+r'｜\1』 \2', taggedText)
        
        # add first set of taggings:
        #self.updateWorkingIndicator()
        taggedText = re.sub('『([0-9]+?)｜([^\n『』]*?)』 ([0-9]+?):([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\3,\4)">\2 \3:\4</ref｝\5', taggedText)
        #self.updateWorkingIndicator()
        taggedText = re.sub('『([0-9]+?)｜([^\n『』]*?)』 ([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\3,)">\2 \3</ref｝\4', taggedText)
        
        # fix references without verse numbers
        # fix books with chapter 1 ONLY; oneChapterBook = [31,57,63,64,65,72,73,75,79,85]
        #self.updateWorkingIndicator()
        taggedText = re.sub('<ref onclick="bcv\((31|57|63|64|65|72|73|75|79|85),([0-9]+?),\)">', r'<ref onclick="bcv(\1,1,\2)">', taggedText)
        # fix references of chapters without verse number; assign verse number 1 in taggings
        #self.updateWorkingIndicator()
        taggedText = re.sub('<ref onclick="bcv\(([0-9]+?),([0-9]+?),\)">', r'<ref onclick="bcv(\1,\2,1)">＊', taggedText)
        
        # check if verses following tagged references, e.g. Book 1:1-2:1; 3:2-4, 5; Jude 1
        p = re.compile('</ref｝[,-–;][ ]*?[0-9]', flags=re.M)
        s = p.search(taggedText)
        while s:
            #self.updateWorkingIndicator()
            taggedText = re.sub('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^\n｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,\7)">\6:\7</ref｝\8', taggedText)
            taggedText = re.sub('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^＊][^\n｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?)([^:0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\2,\6)">\6</ref｝\7', taggedText)
            taggedText = re.sub('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^＊][^\n｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\2,\6)">\6</ref｝:\7', taggedText)
            taggedText = re.sub('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">(＊[^\n｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?)([^:0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,1)">＊\6</ref｝\7', taggedText)
            taggedText = re.sub('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">(＊[^\n｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,1)">＊\6</ref｝:\7', taggedText)
            s = p.search(taggedText)
        
        # clear special markers
        #self.updateWorkingIndicator()
        taggedText = re.sub('『[0-9]+?|([^\n『』]*?)』', r'\1', taggedText)
        taggedText = re.sub('(<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9]+?\)">)＊', r'\1', taggedText)
        taggedText = re.sub('</ref｝', '</ref>', taggedText)
        taggedText = taggedText[:-1]
        return taggedText

    def extractAllReferences(self, text, tagged=False):
        if not tagged:
            taggedText = self.parseText(text)
        else:
            taggedText = text
        return [literal_eval(m) for m in re.findall('bcv(\([0-9]+?,[0-9]+?,[0-9]+?\))', taggedText)] # return a list of tuples (b, c, v)

    def parseFile(self, inputFile):
        # set output filename here
        outputFile = 'output_' + inputFile
        
        # open file and read input text
        try:
            f = open(inputFile,'r')
        except:
            print("File note found! Please make sure if you enter filename correctly and try again.")
            exit()
        newData = f.read()
        f.close()
        
        # parse the opened text
        newData = self.parseText(newData)
        print("Finished parsing file", "\""+inputFile+"\".")
        
        # standardise the format of bible verse references
        # standardisation is running only if user's answer is 'YES' [case-insensitive]
        if self.standardisation.lower() == 'yes':
            newData = self.standardReference(newData)
            print("Verse reference format in file", "\""+inputFile+"\"", "had been standardised.")
        else:
            print("Verse reference format used in file", "\""+inputFile+"\"", "is kept.")

        # save output text in a separate file
        f = open(outputFile,'w')
        f.write(newData)
        f.close()
        print("Output file is saved as \""+outputFile+"\"")

    def parseFilesInFolder(self, folder):
        # create an output directory
        outputFolder = "output_"+folder
        if not os.path.isdir(outputFolder):
            os.mkdir(outputFolder)
        # loop through the directory, running parsing on file(s) only
        fileList = glob.glob(folder+"/*")
        for file in fileList:
            if os.path.isfile(file):
                self.parseFile(file)
        print("All output files are saved in folder", "\""+outputFolder+"\"")

    def startParsing(self, inputName):
        # check if user's input is a file or a folder
        if os.path.isfile(inputName):
            # parse file
            self.parseFile(inputName)
        elif os.path.isdir(inputName):
            # parse file(s) in a directory
            self.parseFilesInFolder(inputName)
        else:
            # input name is neither a file or a folder
            print("\""+inputName+"\"", "is not found!")

"""
END - class BibleVerseParser
"""

if __name__ == '__main__':
    # Interaction with user
    # ask for filename or folder name
    inputName = input("Enter a file / folder name here: ")
    # ask if standardising abbreviations and reference format
    standardisation = input("Do you want to standardise the format of all bible verse references? [YES/NO] ")

    # create an instance of BibleVerseParser
    Parser = BibleVerseParser(standardisation)
    # start parsing
    Parser.startParsing(inputName)

    # example of using extractAllReferences(text)
    # text = input("Enter text containing verse references: ")
    # verseReferences = Parser.extractAllReferences(text)
    # print(verseReferences)

    # delete object
    del Parser
