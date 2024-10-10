d = {1: "a", 2: "b", 3: "c", 4: "d"}
e = {1: "a", 2: "b", 3: "d"}
print(d.keys())
print(d.values())
print(d.items())
print(d.keys() & e.keys())
print(d.items() & e.items())
print(d.keys() - e.keys())
print(d.items() - e.items())
print(d.keys() ^ e.keys())
print(d.items() ^ e.items())

de = [d, e]
f = {}
for dict in de:
    for key in dict:
        f.setdefault(key, []).append(dict[key])
print(f)

# same result
g = {}
for dict in de:
    for key in dict:
        item = g.get(key, "not found")
        if item == "not found":
            g[key] = [dict[key]]
        else:
            item.append(dict[key])
print(g)
