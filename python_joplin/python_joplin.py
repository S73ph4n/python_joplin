import requests, json
"""Main module."""

class Joplin:
    def __init__(self, host='localhost', port=41184, key='', verbose=False):
        """ Set the parameters we need to connect to the API.
        Params:
            * verbose : prints what is being done. For debug purposes.
            * host : host of the Joplin API (usually localhost)
            * port : port of the Joplin API (usually 41181)
            * key : Joplin API key (can be found in Joplin Options / Web Clipper)
        """
        self.verbose=verbose
        self.API_host=host
        self.API_port=port
        if key=='': raise Exception('Please provide the API key.')
        if len(key) != 128: raise Exception('API key should be a 128 alphanumeric string.')
        self.API_key=key
        self.test_connection()

    def test_connection(self):
        """ Tries to connect to the API (to see if parameters are correct).
        Returns the Requests.Response object.
        """
        if self.verbose: print('Testing connection to API...')
        url = 'http://'+self.API_host+':'+str(self.API_port)+'/notes?token='+self.API_key
        if self.verbose: print('GET ', url)
        r = requests.get(url)
        if self.verbose: print('HTTP', r.status_code)
        if r.status_code != 200: raise Exception('Could not connect to API. Please check that the host/port/key is correct.')
        #if self.verbose: print(r.json())
        if self.verbose: print('Connection OK')
        return(r)

    def get_item(self, item_type, item_id='', fields='', subitem_type='', page=1):
        """ Get a item (note, folder, etc.) using Joplin's REST API.
        Ex.: 
        * Get a note's id and title : get_item('notes', 'a1b2c3...', ['id', 'title'])
        * Get the tags associated with a note : get_item('notes', 'a1b2c3...', subitem_type='tags')
        Returns the JSON as a dict.
        N.B. : Will only return one page of results. So, for list of items, please use get_items.
        """
        #Make base url :
        url = 'http://'+self.API_host+':'+str(self.API_port)+'/'+item_type
        if item_id != '': url += '/'+item_id
        if subitem_type != '': url += '/'+subitem_type
        #Append parameters :
        url += '?token='+self.API_key
        if type(fields)==list: fields=','.join(fields)
        if fields != '': url += '&fields='+fields
        url += '&page='+str(page)

        if self.verbose: print('GET ', url)
        r = requests.get(url)
        if self.verbose: print('HTTP', r.status_code)
        if r.status_code == 404: raise Exception('Item not found. Please check the id you provided.')
        if r.status_code != 200: raise Exception('Could not connect to API. Please check that the host/port/key is correct.')
        return(r.json())

    def get_items(self, item_type, item_id='', fields='', subitem_type=''):
        """Get a list of items (notes, tags, folders, etc.). Similar to get_item, but iterates over all pages.
        Returns a list of the JSON dicts."""
        page_n, items = 0, []
        while page_n==0 or page_json['has_more']=='True':
            page_n += 1 
            page_json = self.get_item(item_type, item_id, fields=fields, subitem_type=subitem_type, page=page_n)
            for item in page_json['items']:
                items.append(item)
        return(items)

    def get_note(self, id_note):
        """Get a note from its id.
        Returns a Joplin.Note object."""
        if id_note=='': raise Exception('Please provide the note\'s id.')
        return(self.Note(self, id_note))

    def new_note(self):
        """Creates a note.
        Returns a Joplin.Note object."""
        return(self.Note(self, ''))

    def get_notes(self):
        """ Get a list of all notes.
        Returns a list of Joplin.Note objects."""
        notes_json = self.get_items('notes')
        return([self.get_note(n_j['id']) for n_j in notes_json])

    class Note:
        def __init__(self, jop_API, id_note):
            """ Get the note."""
            self.API = jop_API
            #if id_note=='': raise Exception('Please provide the note\'s id.')
            if id_note=='': 
                id_note=jop_API.post_item('notes')
                if jop_API.verbose: print('No id provided, new note created with id', id_note)
            note_json = jop_API.get_item('notes', id_note, 
                    ['id', 'parent_id', 'title', 'body', 'created_time','updated_time', 
                        'is_conflict', 'latitude', 'longitude', 'altitude', 'author', 
                        'source_url', 'is_todo', 'todo_due', 'todo_completed', 'source', 
                        'source_application', 'application_data', 'order', 'user_created_time', 
                        'user_updated_time', 'encryption_cipher_text', 'encryption_applied', 
                        'markup_language', 'is_shared', 'share_id', 'conflict_original_id'])
            self.id = note_json['id']
            if note_json['parent_id'] != '': 
                self.parent_notebook = jop_API.get_notebook(note_json['parent_id'])
            else:
                self.parent_notebook = None
                    
            self.title = note_json['title']
            self.body = note_json['body']
            self.created_time = note_json['created_time']
            self.updated_time = note_json['updated_time']
            self.is_conflict = note_json['is_conflict']
            self.latitude = note_json['latitude']
            self.longitude = note_json['longitude']
            self.altitude = note_json['altitude']
            self.author = note_json['author']
            self.source_url = note_json['source_url']
            self.is_todo = note_json['is_todo']
            self.todo_due = note_json['todo_due']
            self.todo_completed = note_json['todo_completed']
            self.source = note_json['source']
            self.source_application = note_json['source_application']
            self.application_data = note_json['application_data']
            self.order = note_json['order']
            self.user_created_time = note_json['user_created_time']
            self.user_updated_time = note_json['user_updated_time']
            self.encryption_cipher_text = note_json['encryption_cipher_text']
            self.encryption_applied = note_json['encryption_applied']
            self.markup_language = note_json['markup_language']
            self.is_shared = note_json['is_shared']
            self.share_id = note_json['share_id']
            self.conflict_original_id = note_json['conflict_original_id']
            #self.body_html = note_json['body_html']
            #self.base_url = note_json['base_url']
            #self.image_data_url = note_json['image_data_url']
            #self.crop_rect = note_json['crop_rect']

            self.tags = self.get_tags(self.id)
            self.ressources = self.get_ressources(self.id)

        def push(self):
            """Pushes the notes update(s) to the Joplin API."""
            data={}
            data['id'] = self.id
            data['title'] = self.title
            data['body'] = self.body
            if self.parent_notebook is None:
                data['parent_id'] = ''
            else:
                data['parent_id'] = self.parent_notebook.id
            self.API.put_item('notes', self.id, data) 
            if self.API.verbose: print('Updated note', self.id)

        def delete(self):
            """Deletes the note."""
            self.API.delete_item('notes', self.id)


        def get_tags(self, id_note):
            """ Get tags associated with a note.
            Returns a list of Joplin.Tag objects."""
            tags_json = self.API.get_items('notes', id_note, subitem_type='tags')
            return([self.API.get_tag(t_j['id']) for t_j in tags_json])

        def get_ressources(self, id_note):
            """ Get ressources associated with a note.
            Returns a list of Joplin.Ressource objects."""
            ressources_json = self.API.get_items('notes', id_note, subitem_type='resources')
            return([self.API.get_ressource(r_j['id']) for r_j in ressources_json])

    def get_notebook(self, id_notebook):
        """Get a notebook from its id.
        Returns a Joplin.Notebook object."""
        if id_notebook=='': raise Exception('Please provide the notebooks\'s id.')
        return(self.Notebook(self, id_notebook))

    def new_notebook(self):
        """Creates a notebook.
        Returns a Joplin.Notebook object."""
        return(self.Notebook(self, ''))

    def get_notebooks(self):
        """ Get a list of all notebooks.
        Returns a list of Joplin.Notebook objects."""
        notebooks_json = self.get_items('folders')
        return([self.get_notebook(n_j['id']) for n_j in notebooks_json])

    class Notebook:
        def __init__(self, jop_API, id_notebook):
            """ Get the notebook."""
            self.API = jop_API
            #if id_notebook=='': raise Exception('Please provide the notebooks\'s id.')
            if id_notebook=='': 
                id_notebook=jop_API.post_item('folders')
                if jop_API.verbose: print('No id provided, new notebook created with id', id_notebook)
            notebook_json = jop_API.get_item('folders', id_notebook, ['id', 'parent_id', 'title'])
            self.id = notebook_json['id']
            self.parent_id = notebook_json['parent_id']
            if notebook_json['parent_id'] != '': 
                self.parent_notebook = jop_API.get_notebook(notebook_json['parent_id'])
            else:
                self.parent_notebook = None
            self.title = notebook_json['title']

        def push(self):
            """Pushes the notes update(s) to the Joplin API."""
            data={}
            data['id'] = self.id
            data['title'] = self.title
            if self.parent_notebook is None:
                data['parent_id'] = ''
            else:
                data['parent_id'] = self.parent_notebook.id
            self.API.put_item('folders', self.id, data) 
            if self.API.verbose: print('Updated notebook', self.id)
        
        def delete(self):
            """Deletes the notebook."""
            self.API.delete_item('folders', self.id)

        def get_notes(self):
            """ Get a list of all notes in that notebook.
            Returns a list of Joplin.Note objects."""
            notes_json = self.API.get_items('folders', self.id, subitem_type='notes')
            return([self.API.get_note(n_j['id']) for n_j in notes_json])

    def get_tag(self, id_tag):
        """Get a tag from its id.
        Returns a Joplin.Tag object."""
        return(self.Tag(self, id_tag))

    class Tag:
        def __init__(self, jop_API, id_tag):
            """ Get the tag."""
            #TODO : create it if no id is given.
            if id_tag=='': raise Exception('Please provide the tag\'s id.')
            tag_json = jop_API.get_item('tags', id_tag, ['id', 'parent_id', 'title'])
            self.id = tag_json['id']
            self.parent_id = tag_json['parent_id']
            self.title = tag_json['title']

        def get_notes(self):
            """ Get a list of all notes associated with that tag.
            Returns a list of Joplin.Note objects."""
            notes_json = self.API.get_items('tags', self.id, subitem_type='notes')
            return([self.API.get_note(n_j['id']) for n_j in notes_json])

    def get_ressource(self, id_ressource):
        """Get a ressource from its id.
        Returns a Joplin.Ressource object."""
        return(self.Ressource(self, id_ressource))

    class Ressource:
        def __init__(self, jop_API, id_ressource):
            """ Get the ressource."""
            if id_ressource=='': raise Exception('Please provide the ressource\'s id.')
            ressource_json = jop_API.get_item('resources', id_ressource, ['id', 'title'])
            self.id = ressource_json['id']
            self.title = ressource_json['title']

    def put_item(self, item_type, item_id, data):
        """ Update a item (note, folder, etc.) using Joplin's REST API.
        Takes data as a dict (e.g. {"title":"New title"} to update the title)
        Ex.: 
            * To update a note's title : put_item('notes','a1b2c3...', {'title':'New title'})
        """
        if type(data)!=dict: raise TypeError('put_item only takes the data to update as a dict.')
        #Make base url :
        url = 'http://'+self.API_host+':'+str(self.API_port)+'/'+item_type+'/'+item_id
        #Append parameters :
        url += '?token='+self.API_key

        if self.verbose: print('PUT ', url, '\nwith data :', data)
        r = requests.put(url, json.dumps(data))
        if self.verbose: print('HTTP', r.status_code)
        if r.status_code == 404: raise Exception('Item not found. Please check the id you provided.')
        if r.status_code != 200: raise Exception('Could not connect to API. Please check that the host/port/key is correct.')
        return(r.json())

    def post_item(self, item_type, data={'parent_id':'', 'source':'python_joplin', 'source_application':'com.S73ph4n.python_joplin'}):
        """ Creates an item (note, folder, etc.) using Joplin's REST API.
        Ex.: 
            * To create a note : put_item('notes')
        Returns the id of the new item.
        """
        #Make base url :
        url = 'http://'+self.API_host+':'+str(self.API_port)+'/'+item_type
        #Append parameters :
        url += '?token='+self.API_key

        if self.verbose: print('POST ', url, '\nwith data :', data)
        r = requests.post(url, json.dumps(data))
        if self.verbose: print('HTTP', r.status_code)
        if r.status_code == 404: raise Exception('Item not found. Please check the id you provided.')
        if r.status_code != 200: raise Exception('Could not connect to API. Please check that the host/port/key is correct.')
        return(r.json()['id'])

    def delete_item(self, item_type, item_id):
        """ Delete a item (note, folder, etc.) using Joplin's REST API.
        Ex.: 
            * To delete a note : delete_item('notes','a1b2c3...')
        """
        #Make base url :
        url = 'http://'+self.API_host+':'+str(self.API_port)+'/'+item_type+'/'+item_id
        #Append parameters :
        url += '?token='+self.API_key

        if self.verbose: print('DELETE ', url)
        r = requests.delete(url)
        if self.verbose: print('HTTP', r.status_code)
        if r.status_code == 404: raise Exception('Item not found. Please check the id you provided.')
        if r.status_code != 200: raise Exception('Could not connect to API. Please check that the host/port/key is correct.')
        return(r.text)
