#!/usr/bin/env python3

import sys
import time
import getopt
import configparser
from datetime import datetime
from multiprocessing import Process,Queue

class Config(object):
    def __init__(self,configfile,chengshiname):
        config = configparser.ConfigParser()
        config.read(configfile)
        self._config={}
        if chengshiname is None:
            self._config = dict(config['DEFAULT'])
        elif chengshiname in config:
            self._config = dict(config[chengshiname])
        else:
            raise KeyError
    def get_config(self,src):
        return self._config[src]
    def get_sumRate(self):
        count = 0.00
        for key,value in self._config.items():
            if key == 'jishul' or key == 'jishuh':
                continue
            else:
                count += float(value)
        return count

def getuserdata(userdatafile):
    userdata = []
    with open(userdatafile) as file:
        for l in file.readlines():
            key,value=l.split(',')
            userdata.append([key.strip(),value.strip()])    
    queue1.put(userdata)

def calculator(configfile,chengshiname):
    userdata = queue1.get()
    result = []
    for i in userdata:
        result_single = calculator_single(configfile,chengshiname,i)
        result.append(result_single)
    queue2.put(result)

def calculator_single(configfile,chengshiname,userdata):
    config = Config(configfile,chengshiname)
    JiShuL = config.get_config('jishul')
    JiShuH = config.get_config('jishuh')
    sumRate = config.get_sumRate()
    user_dict = userdata
    shebao = 0.00
    if float(user_dict[1]) > float(JiShuH):
        shebao = float(JiShuH) * sumRate
        d = float(user_dict[1]) - float(JiShuH) * sumRate
    elif float(user_dict[1]) < float(JiShuL):
        shebao = float(JiShuL) * sumRate
        d = float(user_dict[1]) - float(JiShuL) * sumRate
    else:
        shebao = float(user_dict[1])*sumRate
        d = float(user_dict[1]) * (1-sumRate)
    a = d - 3500
    if a<=0:
        b=0
    elif a>0 and a<=1500:
        b=a*0.03
    elif a>1500 and a<=4500:
        b=a*0.1-105
    elif a>4500 and a<=9000:
        b=a*0.2-555
    elif a>9000 and a<=35000:
        b=a*0.25-1005
    elif a>35000 and a<=55000:
        b=a*0.3-2755
    elif a>55000 and a<=80000:
        b=a*0.35-5505
    else:
        b=a*0.45-13505
    shuihou = float(float(user_dict[1])) - b - shebao 
    result = []
    result = [user_dict[0],user_dict[1],format(shebao,".2f"),format(b,".2f"),format(shuihou,".2f"),datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')]
    return result

def dumptofile(outputfile):
        with open(outputfile,'w') as file:
            result = queue2.get()
            for id in result:
                file.write(','.join(id)+'\n')

if __name__=="__main__":
    try:
        queue1 = Queue()
        queue2 = Queue()
        opts, args = getopt.getopt(sys.argv[1:], "hC:c:d:o:", "help")
        for i,v in opts:
            if i in ('-h','--help'):
                print('Usage: calculator.py -C cityname -c configfile -d userdata -o resultdata')
            elif i == '-C':
                chengshiname = v
            elif i == '-c':
                configfile = v
            elif i == '-d':
                userdatafile = v
            elif i == '-o':
                outputfile = v
            else:
                raise ParamenterError 
        process1 = Process(target=getuserdata,args=(userdatafile,))
        process1.start()
        time.sleep(1)
        process2 = Process(target=calculator,args=(configfile,chengshiname.upper()))
        process2.start()
        time.sleep(1)
        Process(target=dumptofile,args=(outputfile,)).start()
        time.sleep(1)
    except:
        print("Parameter Error")


