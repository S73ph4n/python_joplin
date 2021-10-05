from datetime import datetime
import re, click, yaml

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

def clean_ressources(jop_API, confirm=True):
    """Tool to delete orphaned ressources."""
    ress = jop_API.get_ressources()
    for res in ress:
       ns = res.get_notes()#get associated notes
       if ns==[]: #if no associated notes
           if not confirm or click.confirm('Delete ressource '+res.title+' ?', default=False):
               click.echo('Deleting '+res.title)
               res.delete()

def get_yaml(note, key):
    """
    Find a YAML property in a note.
    """
    body = note.body.split('\n')
    i = 0
    while i<len(body):
        if body[i].startswith(key):
            yaml_content = body[i]
            while i+1<len(body) and (body[i+1].startswith(' ') or body[i+1].startswith('\t')):
                    yaml_content += '\n'+body[i+1]
                    i += 1
            return(yaml.safe_load(yaml_content)[key])
        i += 1
    return(None)

def set_yaml(note, yaml_object):
    body = note.body.split('\n')
    i = 0
    while i<len(body):
        if body[i].startswith(key):
            i0 = i
            while i+1<len(body) and (body[i+1].startswith(' ') or body[i+1].startswith('\t')):
                    yaml_content += '\n'+body[i+1]
                    i += 1
            i1 = i
            break
        i += 1
    body = '\n'.join(body[:i0]), dump, '\n'.join(body[i1:])
    note.body = '\n'.join(body)
    note.push()

