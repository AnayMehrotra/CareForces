import sys
import os
import requests
from lxml import html
import json
from pathlib import Path

def getCode(Id,contest):
    Id=str(Id)
    contest=str(contest)
    
    for i in range(0,5):
        solutionPage = requests.get('http://codeforces.com/contest/'+contest+'/submission/'+Id)
        tree = html.fromstring(solutionPage.text)
        if len( tree.xpath('//*[@id="pageContent"]/div[3]/pre/text()')) == 0:
            continue
        break

    if len( tree.xpath('//*[@id="pageContent"]/div[3]/pre/text()')) == 0:
        return -1
    return tree.xpath('//*[@id="pageContent"]/div[3]/pre/text()')[0];

def makeFile(fname,code):
    f=open(fname,"w")
    f.write(code)
    f.close()
    fname=fname.split('/',1)[-1]
    print("Solution:"+fname+" added.")

def Same(File,code):
    return code == open(File).read()

dot={"GNU C++ 4":".cpp","GNU C++11 4":".cpp","GNU C++14":".cpp","GNU C 4":".c","GNU C 4":".c",\
        "Python 2":".py","Python 3":".py","Java 6":".java","Java 7":".java"}

if len(sys.argv) == 0:
    print("Atleast one handle needed!")
    exit(1)

sys.argv=sys.argv[1:]

for user in sys.argv:
    url='http://codeforces.com/api/user.status?handle='+user

    print("User:"+user)
    for i in range(0,3):
        que=requests.get(url).json()
        if que["status"]=="OK":break

    if que["status"]!="OK":
        print("Request failed for "+user+"!")
        continue

    print("Total Submissions:"+str(len(que["result"])))

    if os.path.isfile(user):
        print("File with name \""+user+"\" exists! Skipping handle.")
        continue
    elif not os.path.isdir(user):
        os.mkdir(user)

    for i in range(0,len(que["result"])):
        sub=que["result"][i]
        if sub["verdict"]!="OK":continue
        Id=str(sub["id"])
        contest=str(sub["contestId"])
        index=sub["problem"]["index"]
        extn=dot[sub["programmingLanguage"]]
        code=getCode(Id,contest)
        if(code == -1):
            print("Could not fetch! Contest:"+contest+", submission: "+Id)
            continue
       
        File=user+"/"+contest+"_"+index
        if Path(File+extn).is_file() and not Same(File+extn,code):
            j=2
            while Path(File+"_"+str(j)+extn).is_file() and not Same(File+"_"+str(j)+extn,code):j+=1
            if Path(File+"_"+str(j)+extn).is_file():
                print("Solution:"+File+"_"+str(j)+extn+" already exists, skipped.")
            else: makeFile(File+"_"+str(j)+extn,code)
        elif Path(File+extn).is_file() and Same(File+extn,code):
            File=File.split('/',1)[-1]
            print("Solution:"+File+extn+" already exists, skipped.")
            continue
        else: makeFile(File+extn,code)

    print("Backup complete for user "+user)

exit()
