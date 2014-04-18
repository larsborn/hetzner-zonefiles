import requests
import re
import os
import sys
from BeautifulSoup import BeautifulSoup

base_url = 'https://robot.your-server.de'
zonefiledir = 'zonefiles'

def log(msg, level = ''):
    print '[%s] %s' % (level, msg)

def login(username, password):
    login_form_url = base_url + '/login'
    login_url = base_url + '/login/check'

    r = requests.get(login_form_url)

    r = requests.post(login_url, data={'user': username, 'password': password}, cookies=r.cookies)
    
    # ugly: the hetzner status code is always 200 (delivering the login form
    # as an "error message")
    if 'Herzlich Willkommen auf Ihrer' not in r.text:
        return False
        
    return r.history[0].cookies

def list_zonefile_ids(cookies):
    ret = {}
    last_count = -1
    page = 1
    while last_count != len(ret):
        last_count = len(ret)
        
        dns_url = base_url + '/dns/index/page/%i' % page
        
        r = requests.get(dns_url, cookies=cookies)
        soup = BeautifulSoup(r.text, convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        boxes = soup.findAll('table', attrs={'class': 'box_title'})
        for box in boxes:
            expandBoxJavascript = dict(box.attrs)['onclick']
            zoneid = _javascript_to_zoneid(expandBoxJavascript)
            td = box.find('td', attrs={'class': 'title'})
            domain = td.renderContents()
            ret[zoneid] = domain
        
        page += 1
    return ret

def get_zonefile(cookies, id):
    dns_url = base_url + '/dns/update/id/%i' % id
    r = requests.get(dns_url, cookies=cookies)
    soup = BeautifulSoup(r.text, convertEntities=BeautifulSoup.HTML_ENTITIES)
    textarea = soup.find('textarea')
    zonefile = textarea.renderContents()
    return zonefile
    
def logout(cookies):
    logout_url = base_url + '/login/logout'
    r = requests.get(logout_url, cookies=cookies)
    return r.status_code == 200

def _javascript_to_zoneid(s):
    r = re.compile('\'(\d+)\'')
    m = r.search(s)
    if not m: return False
    return int(m.group(1))

def print_usage():
    print 'Usage: %s [download|update] <username> <password>' % sys.argv[0]

if len(sys.argv) != 4:
    print_usage()
    exit()

command  = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

log('Logging in...')
cookies = login(username, password)

if not cookies:
    print 'Cannot login'
    exit()

if command == 'download':

    log('Requesting list of zonefiles...')
    list = list_zonefile_ids(cookies)

    log('Found %i zonefiles.' % len(list))
    for zoneid, domain in list.iteritems():

        log('Loading zonefile for %s...' % domain)
        zonefile = get_zonefile(cookies, zoneid)
        
        filename = os.path.join(zonefiledir, '%i_%s.txt' % (zoneid, domain))
        log('Saving zonefile to %s...' % filename)
        f = open(filename, 'w+')
        f.write(zonefile)
        f.close()
elif command == 'update':
    pass
else:
    log('Invalid command "%s"' % command)
    print_usage()

log('Logging out')
logout(cookies)
