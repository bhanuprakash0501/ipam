#!/usr/bin/python3

import base64, re, threading, time
import requests, sys, json, ipaddress
import urllib3
import time
import concurrent.futures

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
uname = "username"
passwd = "password"

ibx_urls = ["https://grid1.com", "https://grid2.com", "https://grid3.com"]

cli_credentials = uname + ":" + passwd
wapiv = "v1.2"
header = {"Content-type": "application/json", "Accept": "application/json"}
data = ""


def fetch_data(urls):
    data = requests.get(urls, auth=(uname, passwd), headers=header, verify=False)
    print(data)
    result = json.loads(data.text)  # converting the string output back into list of dictionaries
    return (data)


def url_builder(objtype, objvalue, field, field_value):
    query_urls = [i + "/wapi/" + wapiv + "/" + objtype + ":" + objvalue + "?" + field + "~=" + field_value for i in
                  ibx_urls]
    return query_urls


query_urls = url_builder(objtype="record", objvalue="host", field="name", field_value="gst")

with concurrent.futures.ThreadPoolExecutor() as executor:
    print("Executing mapper")
    print(query_urls)
    res = executor.map(fetch_data, query_urls)
    data = list(res)
    print(data)


def host_rec_json(data):
    results = [i.text for i in data if i.status_code == 200]
