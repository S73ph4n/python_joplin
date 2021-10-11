"""JoplICAL : sync an ICalendar with your notes."""
import os
import time
import click
from icalendar import Calendar, Event
import python_joplin
from python_joplin import tools
from datetime import datetime

CONFIRM = False  # ask before creating each note/ressource
LOOP = True
WAIT_TIME = 60  # wait 60 seconds between each runs

# Environment variables we need:
ENV = {"JOPLIN_TOKEN": ""}

# Date format (ISO only for now)
date_regex = re.compile('[0-9]{4}\-[0-9]{2}\-[0-9]{2} [0-9]{2}\:[0-9]{2}') #matches dates
date_format = "%d/%m/%Y %H:%M:%S" #for datetime.strptime

def get_dates(note):
    """Extract all dates related to a note.
    Returns a list of datetime."""
    dates = []
    if note.todo_due != 0: #if it has a due date:
        dates.append(tools.format_date(note.todo_due))
    dates_in_body = date_regex.findall(note.body)
    for d_i_b in dates_in_body: #if it has a date in the body of the note:
        dates.append(datetime.strptime(d_i_b, date_format))
    return(dates)

# In case the environment variables are not set, let's set them :
for VAR_NAME in ENV.keys():
    ENV[VAR_NAME] = os.getenv(VAR_NAME)
    if not ENV[VAR_NAME]:
        ENV[VAR_NAME] = click.prompt("Enter your " + VAR_NAME, type=str)
    else:
        click.echo(VAR_NAME + " found in the environment.")

while True:
    # Prepare Joplin:
    click.echo("Connecting to Joplin...")
    jop = python_joplin.Joplin(ENV["JOPLIN_TOKEN"])  # Connect to the Joplin API
    click.echo("Joplin connection OK")
    click.echo('Fetching notes...')
    notes = jop.get_notes() #Get the notes
    click.echo('Notes fetched.')

    #Prepare calendar:
    cal = Calendar()
    cal['summary'] = 'Joplin Calendar'

    # Process the notes:
    for note in notes:
        
        if not CONFIRM or click.confirm(
            "Add note " + note.title + " ?", default=False
        ):
            for note_date in get_dates(note):
                event = Event()
                event.add('summary', note.title)
                event.add('description', note.body)
                event.add('dtstart', note_date)
                event.add('duration', 'P1H') #Lasts 1 hour
                cal.add_component(event)

    # Saving calendar:
    f = open('/data/joplin_cal.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

    if not LOOP:
        break
    click.echo("Done. Waiting " + str(WAIT_TIME) + " secs before next run...")
    time.sleep(WAIT_TIME)
