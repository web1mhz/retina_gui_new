import os

def labels_to_names():    
    d = {}

    with open("labels_to_names_seq.txt", encoding="utf-8") as f:

        for line in f:
            (key, val) = line.split(',')
            d[int(key)] = val.strip()
    
    return d

labels_to_names_seq = labels_to_names()
# print(labels_to_names_seq)

a  = list(labels_to_names_seq.values())
print(str(a))