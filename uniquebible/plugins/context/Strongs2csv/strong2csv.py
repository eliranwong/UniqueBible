# flake8: noqa
'''
A utility to extract Strongs Numbers data into a CSV fi1e.
Can enter one or more numbers, i.e. H25 or H356,G217,G875. Saved file will 
be named after the (first) Strongs Number entered, i. e. "H25.csv."
'''


import codecs, os, re, sys
import sqlite3 as sqlite
import strongsData
import getopt

helpTxt = '''
    Enter one or more comma separated Strong's numbers, 
    i.e. H25 or H356,G217,G875. 
    Saved file will be named after the (first) Strongs Number entered, i. e. "H25.csv."
'''


def parseArgs(argv):
    
    # Options
    options = "ho:"

    # Long options
    long_options = ["Help", "Output ="]

    try:
        opts, args = getopt.getopt(argv, options, long_options)
        #print(opts, 'opts', args, 'args')
        if ',' in args:
            argsList = args.split(',')
            argsList = ['[%s]' % a for a in argsList]
        else:
            argsList = ['[%s]' % args]
        
        #print(argsList, 'argList')
        generate(argsList)
    except getopt.GetoptError:
        print ('makeCSV.py <strongs number(s)>, -ho  [outputpath]')
        sys.exit(2)
      
      
def generate(sNumList):

    fn = os.path.join(config.packageDir, "plugins", "context", "Strongs2csv", "av1769s.bib")
    
    #print(snList)

    bibList = []
    csv = ['Idx,Book,Ref.,KJB Verse,KJB Word,Original,Transliteration,Definition']

    #fn = os.path.basename(pth)
    basename = '%s.csv' % sNumList[0][1:-1]
    outputFile = os.path.join(config.packageDir, "plugins", "context", "Strongs2csv", basename)
    csvout = codecs.open(outputFile, 'w', 'utf-8')


    con = sqlite.connect(fn)
    cur = con.cursor()
    cur.execute('SELECT * FROM bible')

    idx = 1
    for row in cur:
        vsTxt = row[2]
        
        if any(sn in vsTxt for sn in sNumList):
            vsTxt = re.sub(r'\[\([HG]\d+\)\]', r'', vsTxt)
            
            vsTxt = re.sub(r'\[\([GH]\d+\)\]|<fn>\d+</fn>|<.+?>|[\r\n]', r'', vsTxt)
            wdGrpList = re.findall(r'[^\]]+\]', vsTxt)
            
            wdList = []
            #snList = []
            owList = []
            transList = []
            defList = []
            wdGrpListFix = []
            for wdGrp in wdGrpList:
                if all(sn not in wdGrp for sn in sNumList):
                    wdGrp = re.sub(r'\[[GH]\d+\]', r'', wdGrp)
                else:
                    wds, sns = wdGrp.split('[')
                    
                    wdGrp = re.sub(r'(\W?\s?)(.+)', r'\1**\2**', wdGrp )
                    wdList.append( '%s' % (re.sub(r'[^\w\s]','', wds).strip()))
                    
                    data = strongsData.strongsData[sns[:-1]]
                    
                    ow = '%s %s' % (sns[:-1], data[0])
                    if not ow in owList:
                        owList.append(ow)
                    if not data[1] in transList:
                        transList.append(data[1])
                    if not data[2] in defList:
                        defList.append(data[2])
                    
                wdGrpListFix.append(wdGrp)
            
            vsTxtFix = ''.join(wdGrpListFix)
            
            wdHits = re.findall(r'[^\s]\*\*([^\[]+)', vsTxtFix)
            hits = re.findall(r'\[[GH]\d+\]', vsTxtFix)
            
            bk, chvs = row[1].split()
            #ch, vs = chvs.split(':')
            
            line = '"%s","%s","%s","%s","%s","%s","%s","%s"' % (idx, bk, row[1], vsTxtFix, ', '.join(wdList), ', '.join(owList), ', '.join(transList), ', '.join(defList))
            #print (line)
            
            csv.append(line)
            
            idx +=1
            
            #print (row)
            ln = '%s\t%s' % (row[1], vsTxt)
            bibList.append(ln)

    #print(csv[1])


    csvout.write('\n'.join(csv))
    csvout.close()
    
    print('CSV Generated')




if __name__ == "__main__":
    if len(sys.argv) > 1:
        parseArgs(sys.argv[1:][0])
    else:
        print('Enter at least one Strong\'s Number (i.e. G25) or -h for help: ')
        
        ip = input()
        if not ip or ip == '-h':
            print(helpTxt)
            sys.exit(0)
        else:
            parseArgs(ip)
            
            
            
