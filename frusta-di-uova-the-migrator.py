# 
# encoding:"utf-8"
#
# Frusta di Uova 1.0
#  
# (c) Boyd Zhang 2011
#
# This is a migrator which archives the blog post
# from blog.sina.com.cn into .WXR XML file.
#
# Licensed under GNU GPL v3
# March 31, 2011

import urllib,re
from string import Template
import os,time
import string


wxr_header = Template("""<?xml version="1.0" encoding="UTF-8"?>
<!-- File: WordPress eXtended RSS -->
<rss version="2.0"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.0/"
>
<channel>
    <title>${blogTitle}</title>
    <link>${blogURL}</link>
    <description></description>
    <pubDate>Tue, 30 Nov 1999 00:00:00 +0000</pubDate>
    <generator>Frusta di uova v1.0 </generator>
    <language>en</language>
""")

wxr_entry = Template("""<item>
  <title>${entryTitle}</title>
  <link>${entryURL}</link>
  <pubDate>${pubDate}</pubDate>
  <dc:creator>${entryAuthor}</dc:creator>
  <category><![CDATA[${category}]]></category>
  <guid isPermaLink="false"></guid>
  <description></description>
  <content:encoded><![CDATA[${entryContent}]]></content:encoded>
  <wp:post_id>${entryId}</wp:post_id>
  <wp:post_date>${postDate}</wp:post_date>
  <wp:post_date_gmt>$(postDate)</wp:post_date_gmt>
  <wp:comment_status>open</wp:comment_status>
  <wp:ping_status>open</wp:ping_status>
  <wp:post_name></wp:post_name>  
  <wp:status>publish</wp:status>
  <wp:post_parent>0</wp:post_parent>
  <wp:menu_order>0</wp:menu_order>
  <wp:post_type>post</wp:post_type>
  <wp:post_password></wp:post_password>
  <wp:is_sticky>0</wp:is_sticky>
  <wp:postmeta>
    <wp:meta_key></wp:meta_key>
    <wp:meta_value><![CDATA[]]></wp:meta_value>
  </wp:postmeta>
</item>
""")

wxr_footer = """
</channel>
</rss>
"""

def home_link(uhtml):
  prog = re.compile("http://blog.sina.com.cn/((u/[0-9]{10})|([0-9a-z]{3,24}))\">首页")
  res = prog.search(uhtml)
  if(res):
    return uhtml[res.start():res.end()-8]
  else:
    return ""

def blog_title(uhtml):
  prog = re.compile(r"<span id=\"blognamespan\">(.){1,24}</span>")
  res = prog.search(uhtml)
  if(res):
    return uhtml[res.start()+24:res.end()-7]
  else:
    return ""

def author(uhtml):
  prog = re.compile(r"<strong id=\"ownernick\">(.){2,40}</strong>")
  res = prog.search(uhtml)
  if(res):
    return uhtml[res.start()+23:res.end()-9]
  else:
    return ""
	
def prev_link(uhtml):
  #the link of the previous article
  res = re.search("<span class=\"SG_txtb\">前一篇：</span><a href=\"", uhtml)
  if(res):
    prev_s = res.end()
    prev_e = prev_s + uhtml[prev_s:].find("\">")
    prev_link = uhtml[prev_s:prev_e]
    return prev_link
  else:
    return ""

def nxt_link(uhtml):  
  #the link of the next article
  res = re.search("<span class=\"SG_txtb\">后一篇：</span><a href=\"", uhtml)
  if(res):
    nxt_s = res2.end()
    nxt_e = nxt_s + uhtml[nxt_s:].find("\">")
    nxt_link = uhtml[nxt_s:nxt_e]
    return nxt_link
  else:
    return ""

def article_list(uhtml):
  #article list
  res0 = re.search(r"http://blog.sina.com.cn/s/articlelist_[0-9]{10}_0_1.html", uhtml)
  if (res0):
    link_end  = res0.start() + uhtml[res0.start():].find("\"")
    article_list_link = uhtml[res0.start():link_end]
    return article_list_link
  else:
    return ""

def content(uhtml):
  #content
  content_s = re.search("<!-- 正文开始 -->", uhtml).end()
  content_e = re.search("<!-- 正文结束 -->", uhtml).start()
  content = uhtml[content_s:content_e]
  return content
  
def post_and_pub_date(uhtml):
  #publish date
  time_s = re.search("time SG_txtc\">\(", uhtml).end()
  time_e = time_s + uhtml[time_s:].find(")</span>")
  post_date = uhtml[time_s:time_e]
  pub_time_tuple = time.strptime(post_date, "%Y-%m-%d %H:%M:%S")
  pub_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", pub_time_tuple)
  return post_date, pub_date

def title(uhtml):
  #title of article
  title_s = re.search(r"titName SG_txta\">", uhtml).end()
  title_e = title_s + uhtml[title_s:].find("</h2>")
  title = uhtml[title_s:title_e]
  title = string.replace(title, "&nbsp;", " ")
  return title

def main():
  #read the latest entry url
  entry_url = raw_input("Please input the URL of your first blog post:\n")
  entry_id = 1
  
  usock = urllib.urlopen(entry_url)
  uhtml = usock.read()
  usock.close()
  
  wh = wxr_header.safe_substitute(blogTitle=blog_title(uhtml), blogURL = home_link(uhtml))
 
  [post_date, pub_date] = post_and_pub_date(uhtml) 
  
  we = wxr_entry.safe_substitute(entryTitle = title(uhtml), entryURL = entry_url,\
    entryAuthor = author(uhtml), category = "", entryContent = content(uhtml), entryId = entry_id, \
    postDate = post_date, pubDate = pub_date)
  
  print entry_id
  print "\n"
  
  tmp = wh + we
  
  wxr_xml = open(os.path.expanduser("~\\Desktop\\blog_archive.xml"),"w")
  wxr_xml.write(tmp)
  wxr_xml.close()
  
  prevurl = prev_link(uhtml)
  
  #continues to retrieve the previous post until the earliest one
  while(prevurl):
    print prevurl
    usock = urllib.urlopen(prevurl)
    uhtml = usock.read()
    usock.close()
    
    [post_date, pub_date] = post_and_pub_date(uhtml)
    entry_id = entry_id + 1
    
    we_prime = wxr_entry.safe_substitute(entryTitle = title(uhtml), entryURL = prevurl,\
      entryAuthor = author(uhtml), category = "", entryContent = content(uhtml), entryId = entry_id, \
      postDate = post_date, pubDate = pub_date)
    
    wxr_xml = open(os.path.expanduser("~\\Desktop\\blog_archive.xml"),"a")
    wxr_xml.write(we_prime)
    wxr_xml.close()   

    prevurl = prev_link(uhtml)
    print entry_id
    print "\n"
    
  wxr_xml = open(os.path.expanduser("~\\Desktop\\blog_archive.xml"),"a")
  wxr_xml.write(wxr_footer)
  wxr_xml.close()
  
  print "Finished exporting to blog_archive.xml at your desktop folder.\n"
  
if __name__=="__main__":
  main()
