import urllib, json
        
class Connection(object):
    def __init__(self):
        self.baseUrl = 'http://www.themagpi.com/mps_api/mps-api-v1.php'
    
    def getQueryResponse(self, params):
        f = urllib.urlopen(self.baseUrl + "?%s" % urllib.urlencode(params))
        return json.loads(f.read())
    
class Issues(object):
    def __init__(self, html=False):
        self.con = Connection()
        response = self.con.getQueryResponse({'mode':'list_issues','html':str(html).lower()})
        self.status = response['status']
        self.data = response['data']
    
    def getIssueByTitle(self, title):
        for issue in self.data:
            if issue['title'] == str(title):
                return issue    
            
class Articles(object):
    def __init__(self, issue_id, html=False):
        self.con = Connection()
        response = self.con.getQueryResponse({'mode':'list_articles', 'issue_id':issue_id, 'html':str(html).lower()})
        self.status = response['status']
        self.data = response['data']
        

    
    
    
    
    