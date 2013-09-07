import mps_api as mps

for article in mps.Articles(mps.Issues().getIssueByTitle('13')['id'], True).data:
    print article['title']
    
    
# this is a quick example, as I was testing it out