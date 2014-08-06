## Pecosys

Pecosys (aka PElican COmment SYStem) is a blog comment system dedicated to
[Pelican](http://docs.getpelican.com), a static site generator, written in
Python, that requires no database or server-side logic. Consequently most
people use hosting services like Disqus to manage blog comments. Pecosys
brings a different approach by making comments part of the static blog. I feel
this approach is in line with strong ideas which stand behind static blogs:

-    own your data, don't delegate to 3rd-party, 
-    be able to rebuild the entire blog offline.

Pecosys is made of three parts:

-    Pelican plugin adds approved comments to generated pages. A comment is a markup file (Markdown or RST) containing metadata like author, published date, article link and the content. 
-    Pelican template is extended to provide a form at the bottom of each article. This is an usual comment posting form. Since Pelican has no server-side logic submitting the form is linked to Pecosys server through the HTTP server. It can be done using Apache proxy module or easier with NGinX. 
-    Pelican server receives submitted comments and it manages approval process by interacting with blog administrator via email. 

### Pecosys plugin

CaCause is the Pelican plugin for managing blog comments. Comments are part of the blog and they're stored on disk. Thus they can be managed by version control GIT. For using CaCause you have to create a dedicated directory and to customize Pelican configuration. 

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
    

**Example**

Run Pelican blog under **site** directory. 

### Pecosys template

**TODO**

### Pecosys server

The server is written in PYTHON and it must be linked to HTTP server in order to process form submission. If you use APACHE, it can be performed using PROXY module. If you use NginX, I provide a configuration sample under **nginx** directory. 