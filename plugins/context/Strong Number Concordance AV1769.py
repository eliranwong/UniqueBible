import config, re, os


def search(sNumList):

    import sqlite3
    fn = os.path.join("plugins", "context", "Strongs2csv", "av1769s.bib")
    con = sqlite3.connect(fn)
    cur = con.cursor()
    cur.execute('SELECT * FROM bible')

    #csv = ['Idx,Book,Ref.,KJB Verse,KJB Word,Original,Transliteration,Definition']
    csv = []
    wdListAll = []
    verseHits = 0
    snHits = 0
    for row in cur:
        vsTxt = row[2]
        
        if any(sn in vsTxt for sn in sNumList):
            vsTxt = re.sub(r'\[\([HG]\d+\)\]', r'', vsTxt)
            vsTxt = re.sub(r'\[\([GH]\d+\)\]|<fn>\d+</fn>|<.+?>|[\r\n]', r'', vsTxt)
            wdGrpList = re.findall(r'[^\]]+\]', vsTxt)
            
            wdList = []
            wdGrpListFix = []
            for wdGrp in wdGrpList:
                if all(sn not in wdGrp for sn in sNumList):
                    wdGrp = re.sub(r'\[[GH]\d+\]', r'', wdGrp)
                else:
                    wds, *_ = wdGrp.split('[')
                    #wdGrp = re.sub(r'(\W?\s?)(.+)', r'\1**\2**', wdGrp )
                    wdGrp = re.sub(r'(\W?\s?)(.+)', r'\1<z>\2</z>', wdGrp )
                    if wds:
                        wdList.append( '%s' % (re.sub(r'[^\w\s]','', wds).strip()))
                    
                wdGrpListFix.append(wdGrp)
            
            vsTxtFix = ''.join(wdGrpListFix)
            
            #wdHits = re.findall(r'[^\s]\*\*([^\[]+)', vsTxtFix)
            snHits += len(re.findall(r'\[[GH]\d+\]', vsTxtFix))
            #', '.join(wdList)
            wdListAll += wdList
            
            line = """<ref onclick="document.title='MAIN:::{0}'">({0})</ref> {1}""".format(row[1], vsTxtFix)
            
            csv.append(line)
            verseHits +=1
    
    return (verseHits, snHits, list(set(wdListAll)), csv)


if config.pluginContext:
    if re.match("^[GH][0-9]+?$", config.pluginContext):
        sNumList = ["[{0}]".format(config.pluginContext)]
        verseHits, snHits, uniqueWdList, verses = search(sNumList)
        html = "<h2>{0} x {2} Hit(s) in {1} Verse(s)</h2><h3>Unique translation:</h3><p>{3}</p><h3>Verses:</h3><p>{4}</p>".format(config.pluginContext, verseHits, snHits, ", ".join(uniqueWdList), "<br>".join(verses))
        config.contextSource.openPopover(html=html)
    else:
        config.mainWindow.displayMessage("Selected text is not a Strong's number!")
else:
    config.contextSource.messageNoSelection()
