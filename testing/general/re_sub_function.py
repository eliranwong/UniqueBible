import re

def func(match):
    print(match.groups()) # ('b', 'd')
    fullString = match.group()
    b = match.group(1)
    d = match.group(2)
    print(fullString, b, d) # abcde b d
    return b+d

p = re.compile("a(b)c(d)e")
newText = p.sub(func, "abcde")
print(newText) # bd
