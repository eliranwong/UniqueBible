import re

def func(match):
    value = match.group()
    if value.islower():
        return value.upper()
    elif value.isupper():
        return value.lower()
    return value

p = re.compile('[a-zA-Z]')
newText = p.sub(func, input("Enter a string here: "))
print(newText)
