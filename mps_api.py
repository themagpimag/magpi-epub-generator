import urllib, json
        
class Connection(object):
    '''Connection class to deal directly with passing the query string to the server side api, and return the decoded response'''
    def __init__(self):
        self.baseUrl = 'http://www.themagpi.com/mps_api/mps-api-v1.php'
    
    def getQueryResponse(self, params):
        '''Send the encoded parameters, and return the decoded response'''
        f = urllib.urlopen(self.baseUrl + "?%s" % urllib.urlencode(params))
        response = json.loads(f.read())
        self.status = response['status']
        return response
    
class Issues(object):
    '''
    Holds a list of issues, along with their respective data:
    self.con.status    :    status response returned by the server
    self.data          :    data returned by the server
    self.data[i]       :    an issue. These are not necessarily stored in a logical order
    
    Each issue in self.data is a dictionary containing the following information:
    (where issue = self.data[i])
    issue['id']        :    the id of that particular issue. This is used server side, and is not the issue number
    issue['title']     :    the issue number
    issue['date']      :    date the issue was published online
    issue['url']       :    url of the online issue page
    issue['issuu']     :    url of the issue's issuu page
    issue['pdf']       :    url of download the issue pdf
    issue['cover']     :    url of the issue's cover image
    issue['editorial'] :    the editorial text
    '''
    def __init__(self, html=True):
        self.con = Connection()
        response = self.con.getQueryResponse({'mode':'list_issues','html':str(html).lower()})
        self.data = response['data']
    
    def getIssueByTitle(self, title):
        '''Returns the issue with the specified title (issue number)'''
        for issue in self.data:
            if issue['title'] == str(title):
                return issue    
            
class Articles(object):
    '''
    Holds a list of articles in a particular issue, along with their respective data:
    self.con.status    :    status response returned by the server
    self.data          :    data returned by the server
    self.data[i]       :    an article. These are not necessarily stored in a logical order
    
    Each article in self.data is a dictionary containing the following information:
    (where article = self.data[i])
    article['id']        :    the id of that particular article
    article['title']     :    the article title
    article['date']      :    date the article was published online (corresponding to the issue date)
    article['url']       :    url of the online article
    article['header']    :    url of the article's header image
    article['content']   :    the article content
    '''
    def __init__(self, issue_id, html=True):
        self.con = Connection()
        response = self.con.getQueryResponse({'mode':'list_articles', 'issue_id':issue_id, 'html':str(html).lower()})
        self.data = response['data']
        

    
    
    
    
    