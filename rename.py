import csv
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from collections import Counter
import pprint

with open("store.csv") as f:
    data = list(csv.reader(f))

for idx in range(len(data)):
    data[idx][0] = Path(data[idx][0])
    year = data[idx][0].parent.stem
    data[idx].append(year)

for file in data:
    og = file[0]
    folder_path = file[0].parent / f"2PH_PRELIM_{file[-1]}_{file[1]}"
    file_path = folder_path / f"2PH_PRELIM_{file[-1]}_{file[1]}_0{file[-3]}{file[-2]}.pdf"
    folder_path.mkdir(parents=True, exist_ok=True)
    og.rename(file_path)
    print(f"{og} -> {file_path}")


# for file in range(len(data)):
#     data[file][0] = Path(data[file][0])
#     year = int(data[file][0].parent.stem)
#     data[file].insert(1,year)


# print(*data,sep="\n")
# data.sort(key=lambda x: (x[1],x[2]))
# dupes = Counter(tuple(i[1:-1]) for i in data)
# print(*[(key,[(i[0][-1],i[1]) for i in list(group)]) for key, group in groupby(sorted(list(dict(dupes).items()),key=lambda x:(x[0],x[1])),key=lambda x:(x[0][0],x[0][1]))],sep="\n")
# fd = []
# for key,group in groupby(data,key=itemgetter(1,2)):
#     grouped = dict([(key2,sorted(list(group2),key=lambda x:x[-1],reverse=True)) for key2,group2 in groupby(group,key=itemgetter(3))])
#     fd.append((key,grouped))

# for key,group in groupby(data,key=itemgetter(1,2)):
#     fd.append((key,list(group)))

# fdd = dict(fd)
# pprint.pprint(fdd)