# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import time
import oc

# Create your views here.
@csrf_exempt
def auto_oc(request):
    return render(request,'index.html',locals())

global miners
miners = []
global info
info = []

@csrf_exempt
def data(request):
    method = request.POST.get('method',None)
    global info
    if method == 'miner_status':
        for miner in miners:
            info = []
            auth = oc.get_auth(miner['ip'], miner['username'], miner['password'])
            info_1 = oc.get_info(miner['ip'], auth)
            info.append({'ip':miner['ip'], 'freq':info_1['ant_data']['bitmain-freq'], 'temp1':info_1['temp_max']})

    elif method == 'ip_search':
        ip = request.POST.get('ip',None)
        for i in info:
            if i['ip'] == ip:
                info = [i]
                break
    elif method == 'miner_info':
        '''
        miner info 'ip username password'
        '''
        miner_info = request.POST.get('miner_info',None)
        for miner in miner_info.split('\n'):
            try:
                info = miner.split(' ')
                miners.append({'ip':info[0], 'username':info[1], 'password':info[2]})
            except Exception as e:
                pass
        info = [{'msg':'ok'}]
    elif method == 'temp_set':
        temp_set = request.POST.get('temp_set',None)
        info = temp_set.split(' ')
        low_temp = info[0]
        high_temp = info[1]
        term = info[2]
        oc.change_freq(miners, low_temp, high_temp, term)
        info = [{'msg':temp_set}]

    response = HttpResponse()
    # response['Content-Type'] = "text/javascript"
    rjson = json.dumps(info)
    response.write(rjson)
    return response
