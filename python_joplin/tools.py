from datetime import datetime
import click, yaml

def format_date(timestamp_ms):
    """Formats a Joplin timestamp into a datetime object."""
    return(datetime.fromtimestamp(timestamp_ms/1000.))

def format_timestamp(dt_object):
    """Formats a datetime object into a Joplin timestamp."""
    return(int(datetime.timestamp(dt_object))*1000)

def clean_ressources(jop_API, confirm=True): #TODO: test
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
    (Gets the first occurrence of a property.)
    """
    body = note.body.split('\n')
    i = 0
    while i<len(body):
        if body[i].startswith(key):
            #print(i)
            yaml_content = body[i]
            while i+1<len(body) and (body[i+1].startswith(' ') or body[i+1].startswith('\t')):
                    yaml_content += '\n'+body[i+1]
                    i += 1
            #print(i)
            return(yaml.safe_load(yaml_content)[key])
        i += 1
    return(None)

def set_yaml(note, key, value):
    """
    Set some YAML in a note.
    (Changes all occurences of a property.)
    """
    body = note.body.split('\n')
    dump = yaml.dump({key: value})
    i, i0 = 0,  None
    while i<len(body):
        if body[i].startswith(key):
            i0 = i
            while i+1<len(body) and (body[i+1].startswith(' ') or body[i+1].startswith('\t')):
                    i += 1
            i1 = i
            body = '\n'.join(body[:i0]) + '\n' + dump + '\n'.join(body[i1+1:]) #concatenate with the YAML dump
            body = body.split('\n')
            i += len(dump.split('\n')) - 2
        i += 1
    if i0==None: #if we couldn't find it:
        note.body = '\n'.join(body) + '\n' +  dump #append it at the end
    else:
        note.body = '\n'.join(body)
    note.push()

