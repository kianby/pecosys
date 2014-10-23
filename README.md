## Pecosys

Pecosys (aka PElican COmment SYStem) is a blog comment system dedicated to
[Pelican](http://docs.getpelican.com), a static site generator, written in
Python, that doesn't require any database or server-side logic. Consequently most
people use hosting services like Disqus to manage blog comments. Pecosys
brings a different approach by making comments part of the static blog. I feel
this approach is in line with static blogs philosophy:

-    protect your data ; do not delegate to 3rd-party services,
-    store things in plain text files, (making version control possible),
-    be able to rebuild the entire blog offline.

Pecosys intends to use email to communicate with the blog administrator.  Email
is no more hype but I'm an old-school guy ;-) Email is reliable and an
universal way to discuss. You can answer from home using your email client,
from work using a webmail or from your smartphone. Pecosys makes an intensive
usage of  **email** and **GIT**.

###  Features overview

Pecosys's main feature is comment management.

Here is the workflow:

-    Readers can submit comments via a comment form embedded in blog pages
-    Blog administrator receives an email notification from Pecosys when a
     comment is submitted
-    Blog administrator can approve or drop the comment by replying to
     Pecosys
-    Pecosys creates approved comment as a Markdown file and commit to GIT.
     Optionally, Pecosys can launch Pelican publishing process to update the
     blog

Moreover Pecosys has an additional feature: readers can subscribe to further
comments for a post if they have provided an email.

Pecosys is internationalized (english and french).

### Technically speaking, how does it work?

Pelican offers to write blog posts in a markup language as Mardown or RST.
Publishing is the process where Pelican produces a bunch of HTML resources
(page, stylesheets) from markup resources. Then a simple HTTP server is needed
to serve static pages.

Pecosys tries to be as less intrusive as possible. A dedicated email is
assigned to Pecosys to interact with blog administrator and blog subscribers.

By default, Pelican proposes a comment template to interact with Disqus.
Pecosys requires to add a similar template to the Pelican blog. This template
is straightforward. It contains a form, appearing at the bottom of each post,
to submit comments with following data:

-    Surname
-    Email (not mandatory)
-    Web site (not mandatory)
-    Comment in Markdown language (or plain text)
-    A check box to subscribe to further comments for this post

Some JavaScript code posts the form to a local URL bound to... Pecosys.

I can guess two questions:

*So the blog needs a server-side language?*
- Right! Pecosys is written in Python and it uses Flask Web framework. You
  keeps on serving static pages for the blog but you have to link two URL with
  Pecosys. If you use NginX or Apache2 (with Proxy modules), it's not a big
  deal.

*How do you block spammers?*
- That's a huge topic. Current comment form is basic: no captcha support but a honey
  pot. Nothing prevents from improving the template with JavaScript libs to do more
  complex things.

Back to explanations!

Once the comment is posted to Pecosys, an email is sent to the blog
administrator. Depending on administrator's answer the comment is discarded or
published.  Publishing is possible because the blog is versioned by GIT.
Pecosys maintainss its own copy of the blog and it creates a comment by adding
plain text files to the blog sources and committing to GIT.

*Is GIT a strong requirement?*
- Absolutely! Pelican's blogs are thought to be versioned. And GIT is the must.
  Pecosys likes centralized GIT workflow where writers commit to a barebone GIT
  repository and Pecosys pulls and pushes to the same.

*You talk about subscribers. How does it run?*
- Readers have the choice to subscribe at the time they submit a comment.
  Pecosys stores subscriber data inside a light database (TinyDB). When a
  comment is approved for the same post, Pecosys sends an email notification to
  all subscribers to recall article link and to provide an unsubscribe link.
  That unsubscribe URL is the second link you have to bind at HTTP server level
  with Pecosys.

From software architecture point of view, Pecosys is made of three parts:

-    Pelican plugin: it processes comment markup files on Pelican build to
     generate HTML pages.
-    Pelican template: it provides a comment form at the bottom of each
     article.
-    Pecosys server: it receives submitted comments and manages approval
     process by interacting with blog administrator by email. It drives GIT
     commits and subscribers notifications. It's the big piece.

### Pecosys plugin

CaCause is the Pelican plugin for managing blog comments. Comments are part of
the blog and they're stored on disk. Thus they can be versioned by GIT. You
have to create a dedicated directory to store comments and to customize Pelican
configuration to declare the plugin.

**Plugin usage**

Customize Pelican configuration defined in *pelicanconf.py* like this:

    # register cacause plugin
    PLUGINS = ['cacause',]

    # configure cacause
    CACAUSE_DIR = "comments"
    CACAUSE_GRAVATAR = True 

Parameters: 

-   Add 'cacause' to the list of enabled plugins
-   *CACAUSE_DIR* is a directory under Pelican root directory where comments
    are stored in markup format.
-   *CACAUSE_GRAVATAR* is a boolean to enable or disable Gravatar support.

**Comment file**

Each comment is a file in REST  or Markdown format (.rst or .md file
extension). The header is used to define comment metadata: author name, author
email, web site, published date.

Here is a sample:

    author: ZNetBlogger
    email: admin@znetblogger.com
    site: http://www.znetblogger.com
    date: 2014-08-04 22:14:12
    url: http://blogduyax.madyanne.fr/supervisor-gestion-de-processus.html
    article: b0e27824a52daadd836953c9259c96b1
    
    Thanks for your post. It should be very helpful. 


Since a comment is nothing more than a plain text file you can add comments in
the same way you write articles. The tricky thing is the article metadata which
is a key to link the comment to the article. Actually it is a MD5 hash of
article relative path. Usually you anwser to a user comment and you already get
get this key in user's comment file. So you can copy and paste to yours.
Another way to do it: use the comment form on the blog itself and let Pecosys
doing the job   

### Pelican template

The blog under **site** directory is a [real example of a Pelican site using
Pecosys](http://blogduyax.madyanne.fr) for comments.

Templates are located under **site/blogduyax/theme/pure-theme/templates**:

-   **article.html** has been modified to embed the comment template
-   **comment.html** is the template defining the form

### Pecosys server

**How does it work?**

The server is written in PYTHON. Pecosys servers acts as an HTTP server
accepting POST requests. Thus it must be linked to HTTP server in order to
process form submission. If you use APACHE, it can be performed using PROXY
module. A sample configuration for NginX is provided under **http** directory. 

An email account is dedicated to Pecosys server. This email is used for
interactions with blog administrator.

GIT is a central piece of Pecosys server. Pecosys get access to a GIT clone of
the blog. When a new comment is posted Pecosys performs two things:

-    a notification email is sent to the blog administrator
-    a new GIT branch is created and the comment is committed into this branch

The blog administrator receives an email describing the comment and he has to
reply. A quick reply is a go for publishing whereas a reply starting with
**NO** means the comment must be discarded. Pecosys reads email subjects to
know the context. So do not change email subject when replying.

Pecosys servers polls email inbox every minute in order to process replies. If
the administrator requests to discard the comment then the comment branch is
deleted. Otherwise the comment branch is merged to the master branch and it is
pushed to origin.

The server configuration is stored in a JSON file. A config named
**config.json** is provided as example. The configuration is divided into four
sections:

-    **global**: language parameter
-    **imap**: authentication parameters to access email inbox.
-    **smtp**: authentication parameters to send emails.
-    **post**: listening address and port for HTTP POST server, sender email
     and administrator email used to send notifications on new comment posting.
     An optional postcommand parameter can be used to intiate Pelican build.
-    **subscription**: unsubscribe URL and sender email to interact with
     subscribers.
-    **git**: this sections contains the path to GIT repository, the
     sub-directory contains comments files and a boolean indicating if a push
     to origin is expected. If you manage GIT in a central workflow you
     probably want to push changes to the bare repository. 

Subscribers are stored in a file **db.json** in the startup directory. 

Which technology is used:

-    [Python](https://www.python.org)
-    [Flask](http://flask.pocoo.org)
-    [TinyDB](https://tinydb.readthedocs.org/en/latest).
-    [Sh](https://pypi.python.org/pypi/sh)
-    [Clize](https://pypi.python.org/pypi/clize)
-    [Markdown](http://daringfireball.net/projects/markdown)

**How to install and run?**

Get the code

    git clone git@github.com:kianby/pecosys.git
    
Go to **server** directory and create your own configuration based on *config.json* 

Install Python dependencies. It's a good habit to create a Python virtual env first.

    pip install -r requirements.txt
    

Start the server

    python pecosys/runserver.py [CONFIG_PATHNAME]


**I recommend testing in a sandbox to validate GIT interactions before going to production.**

Enjoy!
