import re

def func(match):
    value = match.group()
    if value == 'a':
        return 'A'
    elif value == 'A':
        return 'a'
    return value

p = re.compile('[aA]')
newText = p.sub(func, 'Testing AaAaAaAaAaAa')
print(newText)
