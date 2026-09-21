from unicodedata import name
import json
from ntpath import join
import os
path=os.path.join("src","new_chatbi","_init_.py")
# print(path)


pwd=os.getcwd()
# print(pwd)

path=os.path.join("pormpt.json")
with open(path,"rb") as file:
    data=file.read()
text=data.decode("utf-8")
dict=json.loads(text)
for ind in dict["indicators"]:
    print(ind)
