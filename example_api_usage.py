import mps_api as mps

# get the list of issues
issues = mps.Issues()

# get issue 13
issue_13 = issues.getIssueByTitle('13')
issue_13_id = issue_13['id']


# print all the articles' titles
articles_13 = mps.Articles(issue_13_id).data
for article in articles_13:
    print article['title']
    
# definitely see the commented code in mps_api.py

# testing the epub package


import epub, re, os

def cleanString(s):
    rx = re.compile('\W+')
    return rx.sub('', s).strip()

if not os.path.exists('files'):
    os.makedirs('files')
    
book = epub.open_epub('files/test_issue_13.epub', u'w')

for article in articles_13:
    f = open('files/' + cleanString(article['title']) + '.xhtml', 'w+')
    article_content = '<h1>' + article['title'] + '</h1>'
    article_content += article['content']
    f.write(article_content)
    f.close()
    filename = f.name
    manifest_item = epub.opf.ManifestItem(identifier=cleanString(article['title']),
                                          href='text/' + cleanString(article['title']) + '.xhtml',
                                          media_type='application/xhtml+xml')
    book.add_item(filename, manifest_item)
    spine = epub.opf.Spine
    book.opf.spine.add_itemref(cleanString(article['title']))
book.close()

print 'done'