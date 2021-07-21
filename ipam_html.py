#!/usr/bin/python3
# Importing the 'cgi' module
import base64
import cgi
import concurrent.futures
import os
import re
import threading
import time
import time
import ipaddress
import json
import requests
import sys
import urllib3
from bp import dbm

# ### Global Variables start here####
wapiv = "v1.2"
db = dbm.dbm()
(uname, passwd) = db.get_credentials()
header = {"Content-type": "application/json", "Accept": "application/json"}
host_records = {}



# ### Global Variables end here####


def extract_post_data(form):
    pass


# ### this method fetches data from IPAM grids
def fetch_data(urls):
    data = requests.get(urls, auth=(uname, passwd), headers=header, verify=False)
    print(data)
    result = json.loads(data.text)  # converting the string output back into list of dictionaries
    return data


def fetch_data_threading(query_urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        print("Executing mapper")
        print(query_urls)
        res = executor.map(fetch_data, query_urls)
        print("<p>Executor map completed. </p>")
        data = list(res)
        return data


# ### This method builds API URL's for host record type queries
def build_urls(ibx_urls, base_url, records):
    query_urls = []
    par_urls = [base_url + i for i in records if i != ""]
    for i in ibx_urls:
        query_urls.extend([i + j for j in par_urls])
    return query_urls


def select_ibx_urls(form):
    ibx_urls = []
    if form.getvalue("grid1.com"):
        ibx_urls.append("https://grid1.com")
    if form.getvalue("grid2.com"):
        ibx_urls.append("https://grid2.com")
    if form.getvalue("grid3.com"):
        ibx_urls.append("https://grid3.com")
    if len(ibx_urls) == 0:
        print_exit("Select Atleaset 1 GRID..")
    return ibx_urls


def print_input_form():
    print("<h1> IPAM Search..!! </h1>")
    print("<p>Enter multiple entries with new line as seperator..</p>")
    # ### Input form starts here####
    print("<form method='POST' action='hello.py'>")
    print("<p><textarea rows='10' cols='50' name='records'></textarea></p>")
    print("<p> Select IPAM grids to be searched: </p>")
    print("<input type='checkbox' name='grid1.com' checked/> grid1.com")
    print("<input type='checkbox' name='grid2.com' /> grid2.com")
    print("<input type='checkbox' name='grid3.com' /> grid3.com")
    print("<p> Select Type of Query: </p>")
    print("<input type='radio' name='reqtype' value='host_records' checked/> Host records")
    print("<input type='radio' name='reqtype' value='others' /> Others<br /><br /><br />")
    print("<input type='submit' value='Submit' />")
    print("</form")
    # ### Input form ends here####


def print_exit(message=""):
    print(f"<h1>{message} </h1>")
    print("</body></html>")
    exit()


# ### Decodes Request response data. Extracts ipv4, host_name and DNS view fields.
def host_record_processor(data):
    for i in data:
        try:
            host_records_inc = len(host_records)+1
            ipv4 = i["ipv4addrs"][0]["ipv4addr"]
            host_name = i["ipv4addrs"][0]["host"]
            view = i['view']
            host_records[host_records_inc] = {ipv4, host_name, view}
            print(f"<p>{ipv4, host_name, view}</p>")
        except:
            print(f"<p>{str(sys.exc_info()[0])}</p>")
            pass



def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("Content-type: text/html\r\n\r\n")
    # ### HTML BODY starts here####
    print("<html><body>")
    print_input_form()
    if os.environ['REQUEST_METHOD'] == 'GET':
        print_exit("GET METHOD NOTICED")
    # ### extracting post headers start here####
    form = cgi.FieldStorage()
    ibx_urls = select_ibx_urls(form)
    if not form.getvalue("records") or not form.getvalue("reqtype"):
        print_exit("Invalid Data..")
    if form.getvalue("records"):
        records = form.getvalue("records")
        records = records.lower().replace("\r", "")
        records = records.split("\n")
        print("<h1>Inpur records are: " + str(records) + "</h1><br />")
    if form.getvalue("reqtype") == "host_records":
        query_urls = build_urls(ibx_urls, "/wapi/" + wapiv + "/record:host?name~=", records)
        print("<h1>Thanks for choosing Host records..</h1><br />")
        print(f"<p>Build URL's are: {query_urls}")
        data = fetch_data_threading(query_urls)
        # ### Process received data from IBX for host_records type
        [host_record_processor(json.loads(i.text)) for i in data]
        # print(f"<p>{json.dumps(host_records)}</p>")
    if form.getvalue("reqtype") == "others":
        print("<h1>Others not yet supported..</h1><br />")
    # ### HTML BODY ends here####
    print_exit()


if __name__ == "__main__":
    main()
