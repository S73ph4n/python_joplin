from datetime import datetime
import re

date_regex = re.compile('[0-9]{4}\-[0-9]{2}\-[0-9]{2}') #matches dates

def extract_dates(jop_API):
    notes = jop_API.get_notes()
    dates = []
    for note in notes:
        if note.todo_due != 0: 
            dates.append({'date':format_date(note.todo_due), 'id': note.id, 'title':note.title})
        if date_regex.match(note.parent_notebook.title):
            dates.append({'date': date_regex.match(note.parent_notebook.title).group(), 'id': note.id, 'title':note.title})
    return(dates)

def format_date(timestamp_ms):
    """Formats a Joplin timestamp into a datetime object."""
    return(datetime.fromtimestamp(timestamp_ms/1000.))

def format_timestamp(dt_object):
    """Formats a datetime object into a Joplin timestamp."""
    return(int(datetime.timestamp(dt_object))*1000)
