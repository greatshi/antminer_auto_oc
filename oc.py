#!/usr/bin/env python
#coding=utf-8

import urllib  
import urllib2
import re
import time
from collections import OrderedDict

def get_auth(ip, username, password):
	url_top = 'http://' + ip
	realm="antMiner Configuration"
	auth = urllib2.HTTPDigestAuthHandler()
	auth.add_password(realm,url_top,username,password)
	return auth

def get_info(ip, auth):
	url_status = 'http://'+ ip +'/cgi-bin/minerStatus.cgi'
	url_clock = 'http://'+ ip +'/cgi-bin/minerAdvanced.cgi'

	opener = urllib2.build_opener(auth)
	urllib2.install_opener(opener)
	res_data = urllib2.urlopen(url_status).read()
	temp = re.findall('<div id="cbi-table-1-temp">(.*?)</div>', res_data)
	temp_max = 0
	for i in temp:
		if str(i) > temp_max:
			temp_max = str(i)

	res_set = urllib2.urlopen(url_clock).read()
	clock_set = re.findall('<option value="(.*?)">', res_set)
	ant_data = re.findall('ant_data = (.*?);', res_set, re.S)
	true = True
	ant_data = eval(ant_data[0])

	return {'temp_max':temp_max, 'ant_data':ant_data, 'clock_set':clock_set}

def set_miner(ip, auth, info):
	url = 'http://'+ ip +'/cgi-bin/set_miner_conf.cgi'
	opener = urllib2.build_opener(auth)
	urllib2.install_opener(opener)
	pools = info['ant_data']['pools']

	keys = ['_ant_pool1url', '_ant_pool1user', '_ant_pool1pw', '_ant_pool2url', 
	        '_ant_pool2user', '_ant_pool2pw', '_ant_pool3url', '_ant_pool3user', 
	        '_ant_pool3pw', '_ant_nobeeper', '_ant_notempoverctrl','_ant_fan_customize_switch',
	        '_ant_fan_customize_value', '_ant_freq']
	values = [pools[0]['url'], pools[0]['user'], pools[0]['pass'],
	          pools[1]['url'], pools[1]['user'], pools[1]['pass'],
	          pools[2]['url'], pools[2]['user'], pools[2]['pass'],
	          'false', 'false', 'false', '', info['ant_data']['bitmain-freq']]
	data = OrderedDict(zip(keys,values))
	data = urllib.urlencode(data)

	request = urllib2.Request(url, data=data)
	response = urllib2.urlopen(request)

	print 'change result: ' + response.read()

def change_freq(ips, username, password, low_temp, high_temp, term):
	while True:
		for ip in ips:
			auth = get_auth(ip, username, password)
			info = get_info(ip, auth)
			freq = info['ant_data']['bitmain-freq']
			print 'ip: ' + ip + ' temp: ' + info['temp_max'] + ' freq: ' + freq
			if int(info['temp_max']) < low_temp:
				for i in info['clock_set']:
					if int(freq) < int(i):
						info['ant_data']['bitmain-freq'] = i
						set_miner(ip, auth, info)
			elif int(info['temp_max']) > high_temp:
				re_clk = info['clock_set'].reverse()
				for i in re_clk:
					if int(info['temp_max']) > int(i):
						info['ant_data']['bitmain-freq'] = i
						set_miner(ip, auth, info)
		time.sleep(term)

def main():
	ips = ['192.168.1.101']
	username = 'root'
	password = 'root'
	low_temp = 69
	high_temp = 73
	term = 3600
	
	change_freq(ips, username, password, low_temp, high_temp, term)

if __name__ == '__main__':
	main()