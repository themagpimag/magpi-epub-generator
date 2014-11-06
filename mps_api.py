import urllib
import json
import re
import HTMLParser
        
        
class Connection(object):
    """Connection class to deal directly with passing the query string to the server side api,
    and return the decoded response"""
    
    def __init__(self):
        self.baseUrl = 'http://www.themagpi.com/mps_api/mps-api-v1.php'
        self.status = None
    
    def get_query_response(self, params):
        """Send the encoded parameters, and return the decoded response
        Args:
            params (dict): Parameters to pass in the query string
            
        Returns:
            response (dict): JSON decoded from response string
        """
        f = urllib.urlopen(self.baseUrl + "?%s" % urllib.urlencode(params))
        response = json.loads(f.read())
        self.status = response['status']
        return response
    
    
class Post(object):
    """Base object for post data received from the web server. Both issues and articles are posts."""
    
    def __init__(self, data):
        """
        Args:
            data (dict): A dictionary containing all post data
        
        Returns:
            None
        """
        self.data = data
        self.id = data['id']
        self.title = data['title']
        self.date = data['date']
        self.url = data['url']
    
    
class Issue(Post):
    """Represents an issue on the website
    
    Attributes:
        id (str): the id of that particular issue. This is used server side, and is not the issue number
        title (str): the issue number
        date (str): date the issue was published online
        url (str): url of the online issue page
        issuu (str): url of the issue's issuu page
        pdf (str): url of download the issue pdf
        cover (str): url of the issue's cover image
        editorial (str): the editorial text
    """
    
    def __init__(self, data):
        """
        Args:
            data (dict): A dictionary containing all post data
        
        Returns:
            None
        """
        Post.__init__(self, data)
        self.issuu = data['issuu']
        self.pdf = data['pdf']
        self.cover = data['cover']
        self.editorial = data['editorial']
        self.articles = None
        
    def get_articles(self):
        """Get the articles corresponding to this issue
        
        Returns:
            articles
        """
        self.articles = Articles(self.id)
        return self.articles
        
        
class Article(Post):
    """Represents an article within an issue
    
    Attributes:
        id (str): the id of that particular issue. This is used server side, and is not the issue number
        title (str): the issue number
        date (str): date the issue was published online
        url (str): url of the online issue page
        header (str): url of the article's header image
        content (str): the article content
    """
    
    def __init__(self, data):
        """
        Args:
            data (dict): A dictionary containing all post data
        
        Returns:
            None
        """
        Post.__init__(self, data)
        self.header = data['header']
        self.content = data['content']
        self.unescapedTitle = self.get_unescaped_title()
        self.cleanTitle = self.get_clean_title()
        
    def get_unescaped_title(self):
        return HTMLParser.HTMLParser().unescape(self.title)
    
    def get_clean_title(self):
        rx = re.compile('\W+')
        return rx.sub('-', self.unescapedTitle)
    
    
class Issues(object):
    """
    Holds a list of issues
    """
    
    def __init__(self, html=True):
        self.con = Connection()
        response = self.con.get_query_response({'mode': 'list_issues', 'html': str(html).lower()})
        self.issues = []
        for issue in response['data']:
            self.issues.append(Issue(issue))
    
    def get_issue_by_title(self, title):
        """Returns the issue with the specified title (issue number)"""
        for issue in self.issues:
            if issue.title == str(title):
                return issue
            
    def __getitem__(self, key):
        return self.get_issue_by_title(str(key))
    
    def __iter__(self):
        return self.issues


class Articles(object):
    """
    Holds a list of articles in a particular issue
    """

    def __init__(self, issue_id, html=True):
        self.con = Connection()
        response = self.con.get_query_response(
            {'mode': 'list_articles', 'issue_id': issue_id, 'html': str(html).lower()})
        self.articles = []
        if response['status'] == 'ok':
            for article in response['data']:
                self.articles.append(Article(article))
        else:
            print '*Error: ', response['status'], response['data']
            if response['data'] == 'no articles':
                print '      : No articles uploaded to the website in this issue'
    
    def __iter__(self):
        for article in self.articles:
            yield article