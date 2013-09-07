import mps_api as mps

# get the list of issues
issues = mps.Issues()

# get issue 13
issue_13 = issues.getIssueByTitle('13')
issue_13_id = issue_13['id']


# print all the articles' titles
for article in mps.Articles(issue_13_id).data:
    print article['title']
    
# definitely see the commented code in mps_api.py