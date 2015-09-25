I am going to use this as a guiide on how to get all of this running.  This has only been tested in linux so far.  Contact /u/RenderedInGooseFat, if you have difficulties with this.

###WHAT YOU WILL NEED###

A python interpreter.  they can be found here: https://www.python.org/downloads/

PIP.  the installation guide can be found here: https://pip.pypa.io/en/stable/installing/

PhantomJS, unless you are ok with a browser opening every minute or so while the script runs.  The download for that can be found here: http://phantomjs.org/download.html

PyQuery.  You can get it from here as a zip: https://pypi.python.org/pypi/pyquery but I would suggest going through PIP.  Open up a command line and type "pip install pyquery" without the quotes.  If you are on a UNIX machine you will likely need to add sudo to the start of that command unless you are logged in as root for some reason.

Tornado.  Again for this it is best to use pip.  Follow the last set of instructions, and type "pip install tornado".  There is a possiblity your python install may have this already.  

PRAW.  Again you should probably use pip to do this.  "pip install praw".

A praw.ini file.  I included praw.ini.example with this project, that has some instructions, and a basic structure.  You will get the information needed for that file in the next section.

###MAKING THE BOT###

After all of those things are installed, you can start to create the actual bot.  The first step is just creating an account for it to run on.  Just use an username, and password you would like for that.  After you have the account created, log in with that account, and click preferences in the upper right.  If you can't find it, while logged in, go here: https://www.reddit.com/prefs/.  From there, click apps at the top of the page.  If you can't find it, go here: https://www.reddit.com/prefs/apps/.  Click the "Create An App", or "Create Another App" button.  For the name, give it a name liek Game Thread created for /r/steelers, however don't use bot in the name.  Change the type from web app to script.  Type whatever you want in the description.  For the redirect url, just use the url of the sub you will be running it on.  The about URL can be left blank.  then click "Create App".  You should see all of your fields show up, including a new one named secret.  Store the key in secret, as you will need it for the next steps, and you will need it in your praw.ini file.  

Once you have done all of that, start following this guide: http://tsenior.com/2014-01-23-authenticating-with-reddit-oauth/  In step one, the two most important things to change are scope, and client_id. for client_id, use the secret you got from the last step.  For scope, change the url to scope=identity submit edit modposts modconfig save along with everything else needed.  You may not need all of those permissions, but save, submit, and edit are musts, and edit is useful.  Here are the list of all permissions: http://praw.readthedocs.org/en/latest/pages/oauth.html#oauth-scopes

An example URL from step one is:

https://ssl.reddit.com/api/v1/authorize?state=[meaninglessUniqueStringThatWillBeAddToTheRedirectURL]&duration=permanent&response_type=code&scope=identity submit edit modposts modconfig&client_id=[secretFromPreviousStep]&redirect_uri=https://www.reddit.com/r/mySubreddit

It should ask for your reddit login info, so enter it there.  You should then click accept to give access to the account.  It will then redirect to the redirect_uri, and add the state you entered in the last step, along with a code.  You will need the code for the next step, so save it somewhere.  

For step 5, you will need a way to send a POST request.  I would suggest the "advanced Rest Client" add on for chrome, which can be found here: https://chrome.google.com/webstore/detail/advanced-rest-client/hgmloofddffdnphfgcellkdfbfbjeloo?hl=en-US

If you use that, in the top input field, enter https://ssl.reddit.com/api/v1/access_token, then below that, change the type to POST.  Then in the Payload section, enter a string containing this info:

code=[yourCodeFromThePreviousStep]&grant_type=authorization_code&redirect_uri=[yourRedirectURL]&state=[yourUniqueStringFromBeforeAlthougIThinkItCanBeDifferent]&client_id=[yourClientIDFromStep1OfThisGuide]

You should get a response containing JSON, with your access_token, and your refresh_token.  Enters those in your praw.ini, and you are ready to run the scripts.

To run it, just type "python GameThreadCreator.py teamName/Abb phantomJSInstallLocationBinDirectory"

Teamname/Abb isn't well tested, so check in SubGrabber.py, and check what the abbreviation for your sub is, and use that.  for instance, /r/steelers abbreviation is PIT.  You may also need to change the logostring variables in GameThreadCreator.py.  In/r/steelers, we have the team subs pointing at those images, but you may have it set up differently.  Look for homeLogoString, or awayLogoString to see how they are set.  I have been using pycharm as my IDE, and it seems to work pretty well, so I would reccomend that, unless you have a python editor that you like.









