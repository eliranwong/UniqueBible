a = {(1,2,3),(4,5,6)}
b = {(1,2,3),(7,8,9)}
print(a)
print(b)
union = a | b
print(union)
intersection = a & b
print(intersection)
difference = a - b
print(difference)
symmetric_difference = a ^ b
print(symmetric_difference)

c = {(1,2,3),(10,11,12)}
d = {(1,2,3),(13,14,15)}
list = [a, b, c, d]
set = list[0]
for item in list[1:]:
    set = set & item
print(set)
