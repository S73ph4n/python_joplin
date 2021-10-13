"""JopliZot.py : a script to fetch your Zotero Web items and continuously import it to Joplin."""
import os
import time
import click
from pyzotero import zotero
import python_joplin
from python_joplin import tools
import re

CONFIRM = False  # ask before creating each note/ressource
LOOP = True
WAIT_TIME = 60  # wait 60 seconds between each runs

# Environment variables we need:
ENV = {"JOPLIN_TOKEN": "", "JOPLIN_HOST":"localhost", "JOPLIN_PORT":"41184", "ZOTERO_LIBRARY_ID": "", "ZOTERO_API_KEY": "", "ZOTERO_COLLECTION_ID":""}

year_regex = re.compile("[0-9]{4}") 

def format_str(raw):
    """Format a string so it doesn't break the Joplin API calls (happens with some characters)."""
    forbidden_chars = ["\n", "\r", "#", "\\", "'", '"']
    return "".join([c for c in raw if not c in forbidden_chars])
    # return(''.join([c for c in raw if c.isalnum() or c.isspace()]))
    # return(''.join([c for c in raw if c.isprintable()]))


# In case the environment variables are not set, let's set them :
for VAR_NAME in ENV.keys():
    if not os.getenv(VAR_NAME):
        if CONFIRM:
            ENV[VAR_NAME] = click.prompt("Enter your " + VAR_NAME, type=str, default=ENV[VAR_NAME])
    else:
        ENV[VAR_NAME] = os.getenv(VAR_NAME)
        click.echo(VAR_NAME + " found in the environment.")

while True:
    # Prepare Joplin:
    click.echo("Connecting to Joplin...")
    jop = python_joplin.Joplin(ENV["JOPLIN_TOKEN"], host=ENV["JOPLIN_HOST"], port=int(ENV["JOPLIN_PORT"]))  # Connect to the Joplin API
    zot_notebook = jop.get_notebook_by_title("Zotero_Items", create_if_needed=True)  # get the Joplin notebook we need
    click.echo("Joplin connection OK")

    # Prepare PyZotero:
    click.echo("Connecting to Zotero server...")
    zot = zotero.Zotero(ENV["ZOTERO_LIBRARY_ID"], "user", ENV["ZOTERO_API_KEY"])
    click.echo("Zotero connection OK.\nFetching items...")
    if ENV["ZOTERO_COLLECTION_ID"]:
        items = zot.everything(zot.collection_items_top(ENV["ZOTERO_COLLECTION_ID"])) #Get items from the collection
    else:
        items = zot.everything(zot.top()) #Get all items
    click.echo("Items fetched.")

    # Process the items:
    click.echo("Processing items...")
    for item in items:
        if not CONFIRM or click.confirm(
            "Add item " + item["data"]["title"] + " ?", default=False
        ):
            authors = ''
            for crea in item["data"]["creators"]:
                if crea["creatorType"]=="author":
                    if authors != '': #If there's already an author
                        authors += ' et al.'
                        break
                    authors += crea["lastName"] + ', ' + crea["firstName"][0] + '.'
            date = year_regex.search(item["data"]["date"]).group()
            title = authors + ' ' + format_str(item["data"]["title"]) + ' (' + date +')'  # the title for our note
            click.echo("Adding/updating item:" + title)
            note = zot_notebook.get_note_by_title(
                title, create_if_needed=True
            )  # Create note in notebook (or find it if it exists)
            # if note.body != '': continue #if there's already something, let's not change it
            tools.set_yaml(
                note,
                "Link",
                "[See on Zotero Web](" + item["links"]["alternate"]["href"] + ")",
            )
            for prop_name in item["data"].keys():
                tools.set_yaml(note, prop_name, item["data"][prop_name])


            # TODO : add attachments
            # for att in msg.attachments:
            #    if not CONFIRM or click.confirm(
            #        '\tAdd attachment '+att.filename+' ?', default=True
            #    ):
            #        att_jop = jop.new_ressource(att.filename, att.payload)
            #        note.body += '['+att_jop.title+'](:/'+att_jop.id+')'
            note.source = "Zotero via JopliZot"
            note.add_tag_by_title('zotero', create_if_needed=True)
            note.push()  # Push updates to Joplin
    if not LOOP:
        break
    click.echo("Done. Waiting " + str(WAIT_TIME) + " secs before next run...")
    time.sleep(WAIT_TIME)
