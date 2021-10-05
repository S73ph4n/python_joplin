import os, click, markdownify, python_joplin
from imap_tools import MailBox, AND #TODO : use imaplib ?

confirm=True

# Environment variables we need:
ENV = {'JOPLIN_TOKEN':'', 'IMAP_SERVER':'', 'IMAP_USER':'', 'IMAP_PASSWORD':''} 

# In case the environment variables are not set, let's set them :
for VAR_NAME in ENV.keys():
    ENV[VAR_NAME] = os.getenv(VAR_NAME)
    if not ENV[VAR_NAME] : ENV[VAR_NAME] = click.prompt('Enter your '+VAR_NAME, type=str)
    else : click.echo(VAR_NAME+ ' found in the environment.')

#Prepare Joplin:
jop = python_joplin.Joplin(ENV['JOPLIN_TOKEN'], auto_push=False) #Connect to the Joplin API
inbox_notebook = jop.get_notebook_by_title('IMAP_Inbox', create_if_needed=True) #get the Joplin notebook we need
click.echo('Joplin connection OK')

#Prepare IMAP-Tools:
mb = MailBox(ENV['IMAP_SERVER']).login(ENV['IMAP_USER'], ENV['IMAP_PASSWORD'], initial_folder='INBOX') #Connect to IMAP server
click.echo('IMAP connection OK.\nFetching messages...')
messages = mb.fetch(criteria=AND(seen=False), mark_seen=False, bulk=True) #get unread messages
click.echo('Messages fetched.')

#Process the messages:
# ( See https://pypi.org/project/imap-tools/#email-attributes )
for msg in messages:
    note = inbox_notebook.get_note_by_title(msg.from_ + ' : ' + msg.subject, create_if_needed=True) # Create note in notebook (or find it if it exists)
    if note.body != '': continue #if there's already something, let's not change it
    if not confirm or click.confirm('Add message '+msg.object+' ?', default=False):
        note.body = markdownify.markdownify(msg.html, heading_style='ATX')
        for att in msg.attachments: 
            if not confirm or click.confirm('\tAdd attachment '+att.filename+' ?', default=True):
                att_jop = jop.new_ressource(att.filename, att.payload)
                note.body += '['+att_jop.title+']('+att_jop.id+')'
        note.source = 'Email via JoplIMAP'
        note.push() #Push updates to Joplin
