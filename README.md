## Pecosys

Pecosys (aka PElican COmment SYStem) is a blog comment system dedicated to
[Pelican](http://docs.getpelican.com), a static site generator, written in
Python, that requires no database or server-side logic. Consequently most
people use hosting services like Disqus to manage blog comments. Pecosys
brings a different approach by making comments part of the static blog. I feel
this approach is in line with strong ideas which stand behind static blogs:

-    keep your data, do not delegate to 3rd-party services, 
-    store things in plain text files, forget databases, 
-    be able to rebuild the entire blog offline.

Pecosys is made of three parts:

-    Pelican plugin adds approved comments to generated pages. A comment is a markup file (Markdown or RST) containing metadata like author, published date, article link and the content. 
-    Pelican template is extended to provide a form at the bottom of each article. This is a common comment posting form. Since Pelican has no server-side logic submitting the form is linked to Pecosys server through the HTTP server. This link can be performed easily with NginX or Apache. 
-    Pelican server receives submitted comments and it manages approval process by interacting with blog administrator via email. Then the server publishes approved comments by committing a new file to GIT.  

### Pecosys plugin

CaCause is the Pelican plugin for managing blog comments. Comments are part of the blog and they're stored on disk. Thus they can be versioned by GIT. You have to create a dedicated directory and to customize Pelican configuration. 

**Plugin usage**

Customize Pelican configuration defined in *pelicanconf.py* in this way:

    # register cacause plugin
    PLUGINS = ['cacause',]

    # configure cacause
    CACAUSE_DIR = "comments"
    CACAUSE_GRAVATAR = True 

Parameters: 

-   Add 'cacause' to the list of enabled plugins
-   *CACAUSE_DIR* is a directory under Pelican root directory where comments are stored in REST or Markdown format.
-   *CACAUSE_GRAVATAR* is a boolean to enable or disable Gravatar support.

**Comment file**

Each comment is a file in REST  or Markdown format (.rst or .md file extension). The header is used to define comment metadata: author name, author email, web site, published date.

Here is a sample:

    author: ZNetBlogger
    email: admin@znetblogger.com
    site: http://www.znetblogger.com
    date: 2014-08-04 22:14:12
    url: http://blogduyax.madyanne.fr/supervisor-gestion-de-processus.html
    article: b0e27824a52daadd836953c9259c96b1
    
    Thanks for your post. It should be very helpful. 


Since a comment is nothing more than a plain text file you can add comments in the same way you write articles. The tricky thing is article metadata which is a key to link the comment to the article. Actually it is a MD5 hash of article relative path. Usually you anwser to a user comment and you already get get this key in user's comment. So you can copy paste to yours. Another way to do it: use the comment form on the blog itself and let Pecosys doing the work.   

### Pecosys template

The blog under **site** directory is a real example of a Pelican site relying on Pecosys for comments. 

Templates are located under **site/blogduyax/theme/pure-theme/templates**:

-   article.html has been modified to embed the template comment.html
-   comment.html is the template defining the form to post comments

### Pecosys server

**How does it works?**

The server is written in PYTHON. Pecosys servers acts as an HTTP server accepting POST requests. Thus it must be linked to HTTP server in order to process form submission. If you use APACHE, it can be performed using PROXY module. A sample configuration for NginX is provided under **nginx** directory. 

An email account is dedicated to Pecosys server. This email is used for interactions with blog administrator. 

GIT is a central piece of Pecosys server. Pecosys get access to a GIT clone of the blog. When a new comment is posted via the blog performs two things:

-    a notification email is sent to the blog administrator
-    a new GIT branch is created and the comment is committed into this branch

The blog administrator receives an email describing the comment and he has to reply. A quick reply is a go for publishing whereas a reply starting with "NO" means the comment must be discarded. 

Pecosys servers polls its emails inbox every minute in order to process replies. If the administrator requested to discard the comment the comment branch is deleted. Otherwise the comment branch is merged to the master branch and it is eventually pushed to origin.  

Server configuration is stored in a file named **config.json**. The configuration is divided into four sections:

-    **imap**: this section contains authentication parameters to access email inbox.
-    **smtp**: the server sends outgoing emails to the blog administrator when a new comment is posted. This section contains authentication parameters to send emails.
-    **post**: this section contains listening address and port for HTTP POST server, source email and destination email used to send notifications on new comment posting.
-    **git**: this sections contains the path to GIT repository, the sub-directory contains comments files and a boolean indicating if a push to origin is expected. If you manage GIT in a central workflow you probably want to push changes to the central bare repository. 
    

    

