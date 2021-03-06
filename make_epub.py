import epub
import re
import urllib
import mimetypes
import os
import json
import mps_api as mps


class Epub(object):
    def __init__(self, name):
        self.regexImageSource = re.compile(r'''<img .*?src=['"](.*?)['"] ?.*?/>''')
        self.xhtml_template = u'''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>{title}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <!--<link href="../../stylesheet.css" type="text/css" rel="stylesheet"/>-->
  </head>
  <body>
    <h1>{title}</h1>
    {content}
  </body>
</html>'''
        self.defaultMeta = {
            'title': None,
            'language': 'en',
            'publisher': 'The MagPi LTD',
            'dates': [],
        }
        self.book = epub.open_epub(name + '.epub', u'w')
        self.currentPlayOrder = 0
        
    def add_article_content_image(self, m):
        image_source = m.group(1)
        print 'Found image:', image_source.encode('utf-8')
        image_name = image_source.split('/')[-1]
        f_name = urllib.urlretrieve(image_source)[0]
        epub_image_href = 'img/' + image_name
        epub_image_id = image_name.split('.')[0]
        image_mimetype = mimetypes.guess_type(image_name)[0]
        manifest_item = epub.opf.ManifestItem(identifier=epub_image_id,
                                              href=epub_image_href,
                                              media_type=image_mimetype)
        self.book.add_item(f_name, manifest_item)
        return m.group(0).replace(image_source, '../'+epub_image_href)
        
    def get_article_content_with_images(self, content):
        return re.sub(self.regexImageSource, self.add_article_content_image, content)
        
    def add_article(self, article):
        article_content = self.xhtml_template.format(
            title=article.title,
            content=self.get_article_content_with_images(article.content))
        f = open(article.cleanTitle + '.xhtml', 'w+')
        f.write(article_content.encode('UTF-8'))
        f.close()
        article_href = 'text/' + article.cleanTitle + '.xhtml'
        manifest_item = epub.opf.ManifestItem(identifier=article.cleanTitle,
                                              href=article_href,
                                              media_type='application/xhtml+xml')
        self.book.add_item(f.name, manifest_item)
        os.remove(f.name)
        # add item to epub spine
        self.book.opf.spine.add_itemref(article.cleanTitle)
        # add nav point to epub ncx
        nav_point = epub.ncx.NavPoint()
        nav_point.play_order = str(self.currentPlayOrder)
        nav_point.src = article_href
        nav_point.add_label(article.unescapedTitle)
        self.book.toc.nav_map.add_point(nav_point)
        # add page target to epub page list
        page_target = epub.ncx.PageTarget()
        page_target.value = str(self.currentPlayOrder)
        page_target.target_type = 'normal'
        page_target.src = article_href
        page_target.add_label(article.unescapedTitle)
        self.book.toc.page_list.add_target(page_target)
        # increment the playback order counter
        self.currentPlayOrder += 1
        
    def get_meta_from_file(self, fname='meta.json'):
        try:
            with open(fname) as f:
                return json.loads(f.read())
        except IOError:
            print 'Meta file does not exist, generating defaults'
            f = open(fname, 'w+')
            f.write(json.dumps(self.defaultMeta))
            f.close()
            return self.defaultMeta
        
    def add_metadata(self):
        meta = self.get_meta_from_file()
        emeta = self.book.opf.metadata
        if meta['title']:
            emeta.add_title(meta['title'])
        if meta['language']:
            emeta.add_language(meta['language'])
        if meta['publisher']:
            emeta.publisher = meta['publisher']
        if meta['dates']:
            emeta.dates = meta['dates']
            
    def add_cover(self, image_source):
        image_name = image_source.split('/')[-1]
        f_name = urllib.urlretrieve(image_source)[0]
        image_ext = image_name.split('.')[-1]
        epub_image_name = 'cover'+image_ext
        epub_image_href = '../' + epub_image_name
        epub_image_id = 'cover'
        image_mimetype = mimetypes.guess_type(image_name)[0]
        manifest_item = epub.opf.ManifestItem(identifier=epub_image_id,
                                              href=epub_image_href,
                                              media_type=image_mimetype)
        self.book.add_item(f_name, manifest_item)
        self.book.opf.guide.add_reference(href=epub_image_href,
                                          ref_type='cover',
                                          title='Cover')

    def make(self, issue):
        # add the meta
        self.add_metadata()
        #self.add_cover(issue.cover)
        # add the editorial
        editorial_data = issue.data.copy()
        editorial_data['header'] = None
        editorial_data['content'] = issue.editorial
        editorial_data['title'] = 'Issue ' + issue.title
        self.add_article(mps.Article(editorial_data))
        # add the articles
        articles = issue.get_articles()
        for article in articles:
            print 'Adding:', article.title.encode('utf-8')
            self.add_article(article)
        # save and close
        self.save()
        
    def save(self):
        self.book.close()

issues = mps.Issues()
for i in range(1, 14):
    e = Epub('The-MagPi-issue-'+str(i)+'-en')
    issueObj = issues.get_issue_by_title(str(i))
    print '\n\nCreating issue', issueObj.title.encode('utf-8')
    e.make(issueObj)
print 'done'