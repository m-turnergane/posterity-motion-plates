import json,urllib.request,urllib.parse,sys,time
UA={'User-Agent':'PosterityArchivist/1.0 (research; box)'}
def get(url):
    r=urllib.request.Request(url,headers=UA); return json.load(urllib.request.urlopen(r,timeout=30))
def search(q,lang='en'):
    u='https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode({'action':'wbsearchentities','search':q,'language':lang,'format':'json','limit':5})
    return [(x['id'],x.get('label'),x.get('description')) for x in get(u)['search']]
for q in sys.argv[1:]:
    print(q,'=>',search(q)); time.sleep(0.3)
