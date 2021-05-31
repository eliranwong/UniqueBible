import sys, re
    
"""
This script is modified from a script downloaded from https://github.com/dovgreenwood/Hebrew-Transliteration on 03FEB2021.
Eliran Wong modified the original script to integrate as a part of a feature in UniqueBible.app.
Modifications made by Eliran Wong:
- Place variables and functions into a class HebrewTransliteration
- Change file input to string input
- Convert character "'" to work with text-to-speech feature in UniqueBible.app
- Take system argument as input string if running standalone
- e.g. python3 transliterate3_modified.py "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ"
    בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ
    bereishit bara elohim eit hashamayim veit ha arets 

Credits of the original script
@author Dov Greenwood
@date March 18, 2020
@description Transliterates Hebrew text from a file into English characters, printing the output.
"""

class HebrewTransliteration:

    #"""DATA STRUCTURES AND FUNCTION DEFINITIONS"""
    
    #The sounds of every letter without a dagesh, including also ending letters.
    #Distinct characters are given to each letter, but are changed to their standardized transliteration in the final output.
    #Changing from Hebrew letter unicode to English parallels isn't strictly speaking necesary, but makes the program more readable.
    letters = {
        0x5D0: 'x',
        0x5D1:'v', 0x5D2:'g', 0x5D3:'d', 0x5D4:'h',
        0x5D5:'w',
        0x5D6:'z', 0x5D7:'ch', 0x5D8:'t', 0x5D9:'y',
        0x5DB:'kh', 0x5DA:'kh',
        0x5DC:'l',
        0x5DE:'m', 0x5DD:'m',
        0x5E0:'n', 0x5DF:'n',
        0x5E1:'s',
        0x5E2:'c',
        0x5E4:'f', 0x5E3:'f',
        0x5E6:'ts', 0x5E5:'ts',
        0x5E7:'q', 0x5E8:'r',
        0x5E9:'sh',
        0x5EA:'t',
    
        0:''
    }
    
    #dagesh and list of transformations
    dagesh = 0x5BC
    altered = {
        'v':'b', 'w':'u',
        'kh':'k', 'f':'p'
    }
    
    #shin/sin extension
    shin = {
        0x5C2:'',
        0x5C1:'h'
    }
    
    #letter pairs that should separated by an apostraphe to increase clarity
    bad_pairs = [['s', 'ch'], ['s', 'kh'], ['t', 'ch'], ['t', 'kh'], ['ts', 'h'], ['s', 'h'], ['sh', 'h']]
    
    
    #short vowel characters
    #kamatz can take on an o or a sound depending on the letter under which it appears
    vowels = {
        0x5B7:'a', 0x5B2:'a', 0x5B3:'a',
        0x5B8:'a', #kamatz
        0x5BA:'o', 0x5B9:'o',
        0x5B4:'i',
        0x5B6:'e', 0x5B1:'e',
        0x5B5:'ei',
        0x5BB:'u',
        0x5B0:"'",
    
        0:''
    }
    
    end_characters = {' ', '\n', '\t', ',', '.', ':'}
    
    def last_index(self, char, chars):
        for i in range(len(chars) - 1, -1, -1):
            if chars[i] == char:
                return i
        return False
    
    def curr_word(self, chars):
        word = []
        for i in range(len(chars) - 1, -1, -1):
            if chars[i] in self.end_characters:
                break
            if chars[i] == '':
                continue
            else:
                word.append(chars[i])
        return word[::-1]
    
    def last_letter(self, word):
        for i in range(len(word) - 1, -1, -1):
            if word[i] in self.letters.values():
                return word[i]
        return False
    
    def last_vowel(self, word):
         for i in range(len(word) - 1, -1, -1):
             if word[i] in self.vowels.values() and word[i]:
                 return word[i]
         return False
    
    def shva_na(self, word):
        if len(word) > 1:
            return False
        return True
    
    def remove_h(self, word):
        if len(word) <= 1 or word[-1] != 'h':
            return False
        if self.last_vowel(word) == 'a' or self.last_vowel(word) == 'ei' or self.last_vowel(word) == 'o':
            return True
        return False
    
    def move_vowel_back(self, word):
        lv = self.last_vowel(word)
        ll = self.last_letter(word)
        return (lv == 'a') and (ll == 'h' or ll == 'ch') and (self.last_index(lv, word) > self.last_index(ll, word))
    
    
    def transliterateHebrew(self, text, tts=True):
        #"""FILE INPUT"""
        
        #made as a map in case more punctuation swaps need to be added
        alt_punc = {':':'.', '.':',', '-':' '}
        
        #file = input('file: ')
        #punc = input('replace punctuation? (y/n): ') == 'y'
        
        #text = ''
        #with open(file, 'r', encoding='utf8') as contents:
        #    text = contents.read()
        #if alt_punc:
        for i in alt_punc:
            text = text.replace(i, alt_punc[i])
        text += ' '
        
        """TRANSLITERATION PROCESS"""
        engl = []
        
        for i in text:
            unic = ord(i)
        
            if unic in self.letters.keys():
                if self.letters[unic] == 'y' and (self.last_vowel(self.curr_word(engl)) == 'i' or self.last_vowel(self.curr_word(engl)) == 'ei'):
                    engl.append('')
                else:
                    engl.append(self.letters[unic])
        
            elif unic == self.dagesh:
                if self.last_letter(self.curr_word(engl)) in self.altered.keys():
                    engl[self.last_index(self.last_letter(self.curr_word(engl)), engl)] = self.altered[self.last_letter(self.curr_word(engl))]
                engl.append('')
        
            elif unic in self.shin:
                engl[self.last_index('sh', engl)] += self.shin[unic]
                engl.append('')
        
            elif unic in self.vowels.keys():
                if self.vowels[unic] == "'" and (not self.shva_na(self.curr_word(engl))):
                    engl.append('')
                    continue
                        #  kamatz, the common exception for the word kol/khol
                if unic == 0x5B8 and (self.last_letter(self.curr_word(engl)) == 'k' or self.last_letter(self.curr_word(engl)) == 'kh'):
                    engl.append('o')
                    continue
                if self.vowels[unic] == 'o' and self.last_letter(self.curr_word(engl)) == 'w':
                    engl = engl[:-1]
                    engl.append('')
                engl.append(self.vowels[unic])
        
            elif i in self.end_characters:
                if self.remove_h(self.curr_word(engl)):
                    engl = engl[:-1]
                    engl.append('')
                if self.move_vowel_back(self.curr_word(engl)):
                    temp = engl[-1]
                    engl[-1] = engl[-2]
                    engl[-2] = temp
                engl.append(i)
        
            else:
                engl.append('')
        
        output = ''
        last = ''
        for i in engl:
            #skip silent letters, alef and ayin
            if i == 'x' or i == 'c' or i == '':
                continue
        
            if [last, i] in self.bad_pairs:
                output += "'"
            if last == i and (not i in self.end_characters) and (not i == ''):
                output += "'"
        
            if i == 'w':
                output += 'v'
            elif i == 'kh':
                output += 'ch'
            elif i == 'q':
                output += 'k'
            elif i == 'sh':
                output += 's'
            elif i == 'shh':
                output += 'sh'
            else:
                output += i
        
            last = i
        
        # Convert some characters to make it work with text-to-speech feature.
        searchReplace = (
            ("'([^aeiou])", r"e\1"),
            ("([aeiou])'([aeiou])", r"\1 \2"),
            ("'([aeiou])", r"\1"),
            ("ch |ch$", "k "),
            ("ch", "h"),
        )
        if tts:
            for search, replace in searchReplace:
                output = re.sub(search, replace, output)
        #print(output)
        return output

if __name__ == '__main__':
    #arguments = sys.argv
    print(sys.argv[1])
    print(HebrewTransliteration().transliterateHebrew(sys.argv[1]))

#    import pprint
#    from HebrewTransliteration import HebrewTransliteration
#    from LexicalData import LexicalData
#    newDict = {}
#    for i in range(70001, 79237):
#        entry = "E{0}".format(i)
#        a, b, c = LexicalData.data[entry]
#        d = HebrewTransliteration().transliterateHebrew(a, tts=False)
#        newDict[entry] = (a, b, c ,d.strip())
#    with open("newETCBCdata.py", "w", encoding="utf-8") as fileObj:
#        fileObj.write(pprint.pformat(newDict))
#    print("done")