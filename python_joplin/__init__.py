"""Top-level package for Python Joplin."""
import json
import requests

__author__ = """S73ph4n"""
__email__ = "example@example.com"
__version__ = "0.1.0"

note_props = [
    "id",
    "parent_id",
    "title",
    "body",
    "created_time",
    "updated_time",
    "is_conflict",
    "latitude",
    "longitude",
    "altitude",
    "author",
    "source_url",
    "is_todo",
    "todo_due",
    "todo_completed",
    "source",
    "source_application",
    "application_data",
    "order",
    "user_created_time",
    "user_updated_time",
    "encryption_cipher_text",
    "encryption_applied",
    "markup_language",
    "is_shared",
    "share_id",
    "conflict_original_id",
]

notebook_props = [
    "id",
    "parent_id",
    "title",
    "created_time",
    "updated_time",
    "user_created_time",
    "user_updated_time",
    "encryption_cipher_text",
    "encryption_applied",
    "parent_id",
    "is_shared",
    "share_id",
]

ressource_props = [
    "id",
    "title",
    "mime",
    "filename",
    "created_time",
    "updated_time",
    "user_created_time",
    "user_updated_time",
    "file_extension",
    "encryption_cipher_text",
    "encryption_applied",
    "encryption_blob_encrypted",
    "size",
    "is_shared",
    "share_id",
]

tag_props = [
    "id",
    "title",
    "created_time",
    "updated_time",
    "user_created_time",
    "user_updated_time",
    "encryption_cipher_text",
    "encryption_applied",
    "is_shared",
    "parent_id",
]


class Joplin:
    """
    A object to represent a Joplin instance.
    """

    def __init__(
        self, key, host="localhost", port=41184, verbose=False, auto_push=False
    ):
        """Set the parameters we need to connect to the API.
        Params:
            * verbose : prints what is being done. For debug purposes.
            * host : host of the Joplin API (usually localhost)
            * port : port of the Joplin API (usually 41181)
            * key : Joplin API key (can be found in Joplin Options / Web Clipper)
            * auto_push : Automatically update notes in Joplin on changes
        """
        self.verbose = verbose
        self.api_host = host
        self.api_port = port
        self.auto_push = auto_push
        if key == "":
            raise Exception("Please provide the API key.")
        if len(key) != 128:
            raise Exception("API key should be a 128 alphanumeric string.")
        self.api_key = key
        self.test_connection()

    def test_connection(self):
        """Tries to connect to the API (to see if parameters are correct).
        Returns the Requests.Response object.
        """
        if self.verbose:
            print("Testing connection to API...")
        url = (
            "http://"
            + self.api_host
            + ":"
            + str(self.api_port)
            + "/notes?token="
            + self.api_key
        )
        if self.verbose:
            print("GET ", url)
        req = requests.get(url)
        if self.verbose:
            print("HTTP", req.status_code)
        if req.status_code != 200:
            if self.verbose:
                print(req.headers)
                print(req.text)
            raise Exception(
                "Could not connect to API. Please check that the host/port/key is correct."
            )
        # if self.verbose: print(req.json())
        if self.verbose:
            print("Connection OK")
        return req

    def get_item(self, item_type, item_id="", fields="", subitem_type="", page=1):
        """Get a item (note, folder, etc.) using Joplin's REST API.
        Ex.:
        * Get a note's id and title : get_item('notes', 'a1b2c3...', ['id', 'title'])
        * Get the tags associated with a note : get_item('notes', 'a1b2c3...', subitem_type='tags')
        Returns the JSON as a dict.
        N.B. : Will only return one page of results. So, for list of items, please use get_items.
        item_type should be plural (notes/tags/folders/etc.)
        """
        # Make base url :
        url = "http://" + self.api_host + ":" + str(self.api_port) + "/" + item_type
        if item_id != "":
            url += "/" + item_id
        if subitem_type != "":
            url += "/" + subitem_type
        # Append parameters :
        url += "?token=" + self.api_key
        if type(fields) == list:
            fields = ",".join(fields)
        if fields != "":
            url += "&fields=" + fields
        url += "&page=" + str(page)

        if self.verbose:
            print("GET ", url)
        req = requests.get(url)
        if self.verbose:
            print("HTTP", req.status_code)
        if req.status_code == 404:
            raise Exception("Item not found. Please check the id you provided.")
        if req.status_code != 200:
            if self.verbose:
                print(req.headers)
                print(req.text)
            raise Exception(
                "Could not connect to API. Please check that the host/port/key is correct."
            )
        return req.json()

    def get_items(self, item_type, item_id="", fields="", subitem_type=""):
        """
        Get a list of items (notes, tags, folders, etc.).
        Similar to get_item, but iterates over all pages.
        Returns a list of the JSON dicts.
        N.B. : item_type should be plural (notes/tags/folders/etc.)
        """
        page_n, items = 0, []
        while page_n == 0 or page_json["has_more"]:
            page_n += 1
            page_json = self.get_item(
                item_type,
                item_id,
                fields=fields,
                subitem_type=subitem_type,
                page=page_n,
            )
            for item in page_json["items"]:
                items.append(item)
        return items

    def get_note(self, id_note):
        """Get a note from its id.
        Returns a Joplin.Note object."""
        if id_note == "":
            raise Exception("Please provide the note's id.")
        return self.Note(self, id_note)

    def get_note_by_title(self, title, create_if_needed=False):
        """Finds a note by its title.
        If create_if_needed is True, will create it if it does not exist.
        """
        search_res = self.search_notes('title:"' + title + '"')
        if len(search_res) > 1:
            raise Exception("Several notes with that title.")
        if len(search_res) == 0 and create_if_needed:
            new_note = self.new_note()
            new_note.__setattr__("title", title, push=False)
            new_note.push()
            return new_note
        if len(search_res) == 1:
            return search_res[0]
        raise Exception("No note by that title.")

    def new_note(self):
        """Creates a note.
        Returns a Joplin.Note object."""
        return self.Note(self, "")

    def get_notes(self):
        """Get a list of all notes.
        Returns a list of Joplin.Note objects."""
        notes_json = self.get_items("notes")
        return [self.get_note(n_j["id"]) for n_j in notes_json]

    def search_notes(self, search_string):
        """
        Returns a list of Joplin.Note objects."""
        notes_json = self.search_items(search_string, item_type="note")
        return [self.get_note(n_j["id"]) for n_j in notes_json]

    class Note:
        """
        A object to represent a Joplin Note.
        """

        tags = []

        def __init__(self, jop_api, id_note):
            """Get the note."""
            # if id_note=='': raise Exception('Please provide the note\'s id.')
            self.api = jop_api
            if id_note == "":
                id_note = jop_api.post_item("notes")
                if jop_api.verbose:
                    print("No id provided, new note created with id", id_note)
            self.id = id_note
            self.pull()

        def __setattr__(self, key, value, push=True):
            """Will only auto-push if Joplin.auto_push is True AND push is True."""
            self.__dict__[key] = value
            if push and self.api.auto_push and key in note_props:
                self.push()

        def pull(self):
            """Pulls the notes update(s) from the Joplin API."""
            note_json = self.api.get_item("notes", self.id, note_props)

            for key in note_json.keys():  # set the attributes :
                self.__dict__[key] = note_json[key]

            if note_json["parent_id"] != "":
                try:
                    self.__setattr__(
                        "parent_notebook",
                        self.api.get_notebook(note_json["parent_id"]),
                        push=False,
                    )
                except:
                    print(
                        "WARNING. Could not set parent_notebook to",
                        note_json["parent_id"],
                        "for note",
                        self.id,
                    )
            else:
                self.__setattr__("parent_notebook", None, push=False)
            self.__setattr__("tags", self.get_tags(), push=False)
            self.__setattr__("ressources", self.get_ressources(), push=False)
            if self.api.verbose:
                print("Updated note", self.id)

        def push(self):
            """Pushes the notes update(s) to the Joplin API."""
            data = {}
            for key in note_props:
                data[key] = self.__dict__[key]

            if self.parent_notebook is None:
                data["parent_id"] = ""
            else:
                data["parent_id"] = self.parent_notebook.id

            self.api.put_item("notes", self.id, data)
            for tag in self.get_tags():  # remove the old tags:
                self.api.delete_item(
                    "tags", item_id=tag.id, subitem_type="notes", subitem_id=self.id
                )
            for tag in self.tags:  # set the new tags
                self.api.post_item(
                    "tags", item_id=tag.id, subitem_type="notes", data={"id": self.id}
                )
            if self.api.verbose:
                print("Updated note", self.id)

        def delete(self):
            """Deletes the note."""
            self.api.delete_item("notes", self.id)

        def get_tags(self):
            """Get tags associated with a note.
            Returns a list of Joplin.Tag objects."""
            tags_json = self.api.get_items("notes", self.id, subitem_type="tags")
            return [self.api.get_tag(t_j["id"]) for t_j in tags_json]

        def get_ressources(self):
            """Get ressources associated with a note.
            Returns a list of Joplin.Ressource objects."""
            ressources_json = self.api.get_items(
                "notes", self.id, subitem_type="resources"
            )
            return [self.api.get_ressource(r_j["id"]) for r_j in ressources_json]

        def new_ressource(self, title, file):
            """Creates a new ressource and appends a link to the note's body."""
            att = self.api.new_ressource(title, file)
            self.body += "[" + att.title + "](:/" + att.id + ")"
            return att.id

        def add_tag_by_title(self, title, create_if_needed=False):
            """Adds a tag to the Note."""
            tag = self.api.get_tag_by_title(title, create_if_needed=create_if_needed)
            self.tags.append(tag)
            self.push()

    def get_notebook(self, id_notebook):
        """Get a notebook from its id.
        Returns a Joplin.Notebook object."""
        if id_notebook == "":
            raise Exception("Please provide the notebooks's id.")
        return self.Notebook(self, id_notebook)

    def get_notebook_by_title(self, title, create_if_needed=False):
        """Finds a notebook by its title.
        If create_if_needed id True, will create it if it does not already exist.
        """
        search_res = self.search_notebooks(title)
        if len(search_res) > 1:
            raise Exception("Several notebooks with that title.")
        if len(search_res) == 0 and create_if_needed:
            new_notebook = self.new_notebook()
            new_notebook.__setattr__("title", title, push=False)
            new_notebook.push()
            return new_notebook
        if len(search_res) == 1:
            return search_res[0]
        raise Exception("No notebook by that title.")

    def new_notebook(self):
        """Creates a notebook.
        Returns a Joplin.Notebook object."""
        return self.Notebook(self, "")

    def get_notebooks(self):
        """Get a list of all notebooks.
        Returns a list of Joplin.Notebook objects."""
        notebooks_json = self.get_items("folders")
        return [self.get_notebook(n_j["id"]) for n_j in notebooks_json]

    def search_notebooks(self, search_string):
        """
        Returns a list of Joplin.Notebook objects."""
        notebooks_json = self.search_items(search_string, item_type="folder")
        return [self.get_notebook(n_j["id"]) for n_j in notebooks_json]

    class Notebook:
        """
        A object to represent a Joplin Notebook.
        """

        def __init__(self, jop_api, id_notebook):
            """Get the notebook."""
            self.api = jop_api
            # if id_notebook=='': raise Exception('Please provide the notebooks\'s id.')
            if id_notebook == "":
                id_notebook = jop_api.post_item("folders")
                if jop_api.verbose:
                    print("No id provided, new notebook created with id", id_notebook)
            self.id = id_notebook
            self.pull()

        def __setattr__(self, key, value, push=True):
            """Will only auto-push if Joplin.auto_push is True AND push is True."""
            self.__dict__[key] = value
            if push and key in notebook_props and self.api.auto_push:
                self.push()

        def pull(self):
            """Pulls the notebook's update(s) from the Joplin API."""
            notebook_json = self.api.get_item("folders", self.id, notebook_props)
            for key in notebook_json.keys():  # set the attributes :
                self.__dict__[key] = notebook_json[key]
            if notebook_json["parent_id"] != "":
                self.__setattr__(
                    "parent_notebook",
                    self.api.get_notebook(notebook_json["parent_id"]),
                    push=False,
                )
            else:
                self.__setattr__("parent_notebook", None, push=False)

        def push(self):
            """Pushes the notebook's update(s) to the Joplin API."""
            data = {}
            for key in notebook_props:
                data[key] = self.__dict__[key]
            if self.parent_notebook is None:
                data["parent_id"] = ""
            else:
                data["parent_id"] = self.parent_notebook.id
            self.api.put_item("folders", self.id, data)
            if self.api.verbose:
                print("Updated notebook", self.id)

        def delete(self):
            """Deletes the notebook."""
            self.api.delete_item("folders", self.id)

        def get_notes(self):
            """Get a list of all notes in that notebook.
            Returns a list of Joplin.Note objects."""
            notes_json = self.api.get_items("folders", self.id, subitem_type="notes")
            return [self.api.get_note(n_j["id"]) for n_j in notes_json]

        def get_note_by_title(self, title, create_if_needed=False):
            """Finds a note by its title within a notebook.
            If create_if_needed is True, will create it if it does not exist.
            """
            search_res = self.api.search_notes(
                'title:"' + title + '" notebook:"' + self.title + '"'
            )
            if len(search_res) > 1:
                raise Exception("Several notes with that title in that notebook.")
            if len(search_res) == 0 and create_if_needed:
                new_note = self.new_note(title=title)
                return new_note
            if len(search_res) == 1:
                return search_res[0]
            raise Exception("No note by that title in that notebook.")

        def new_note(self, title=""):
            """Creates a note in that notebook.
            Returns a Joplin.Note object."""
            note = self.api.Note(self.api, "")
            note.__setattr__("parent_notebook", self, push=False)
            if title != "":
                note.__setattr__("title", title, push=False)
            note.push()
            return note

    def get_tag(self, id_tag):
        """Get a tag from its id.
        Returns a Joplin.Tag object."""
        return self.Tag(self, id_tag)

    def get_tag_by_title(self, title, create_if_needed=False):
        """Finds a tag by its title.
        If create_if_needed is True, will create it if it does not exist.
        """
        search_res = self.search_tags(title)
        if len(search_res) > 1:
            raise Exception("Several notes with that title.")
        if len(search_res) == 0 and create_if_needed:
            new_tag = self.new_tag(title)
            new_tag.__setattr__("title", title, push=False)
            new_tag.push()
            return new_tag
        if len(search_res) == 1:
            return search_res[0]
        raise Exception("No tag by that title.")

    def new_tag(self, title):
        """
        * title : the Tag's title
        """
        id_tag = self.post_item("tags", data={"title": title})
        return self.Tag(self, id_tag)

    def search_tags(self, search_string):
        """
        Returns a list of Joplin.Tag objects."""
        tags_json = self.search_items(search_string, item_type="tag")
        return [self.get_tag(t_j["id"]) for t_j in tags_json]

    class Tag:
        """
        A object to represent a Joplin Tag.
        """

        def __init__(self, jop_api, id_tag):
            """Get the tag."""
            self.api = jop_api
            self.id = id_tag
            if id_tag == "":
                raise Exception("Please provide the tag's id.")
            self.pull()

        def __setattr__(self, key, value, push=True):
            """Will only auto-push if Joplin.auto_push is True AND push is True."""
            self.__dict__[key] = value
            if push and self.api.auto_push and key in tag_props:
                self.push()

        def delete(self):
            """Deletes the Tag."""
            self.api.delete_item("tags", self.id)

        def pull(self):
            """Pulls the tags's update(s) from the Joplin api."""
            tag_json = self.api.get_item("tags", self.id, tag_props)
            for key in tag_json.keys():  # set the attributes :
                self.__dict__[key] = tag_json[key]

        def push(self):
            """Pushes the tag update(s) to the Joplin API."""
            data = {}
            for key in tag_props:
                data[key] = self.__dict__[key]

            self.api.put_item("tags", self.id, data)
            if self.api.verbose:
                print("Updated tag", self.id)

        def get_notes(self):
            """Get a list of all notes associated with that tag.
            Returns a list of Joplin.Note objects."""
            notes_json = self.api.get_items("tags", self.id, subitem_type="notes")
            return [self.api.get_note(n_j["id"]) for n_j in notes_json]

    def get_ressource(self, id_ressource):
        """Get a ressource from its id.
        Returns a Joplin.Ressource object."""
        return self.Ressource(self, id_ressource)

    def search_ressources(self, search_string):
        """
        Returns a list of Joplin.Ressource objects."""
        ressources_json = self.search_items(search_string, item_type="resource")
        return [self.get_ressource(r_j["id"]) for r_j in ressources_json]

    def new_ressource(self, title, file):
        """
        * title : the Ressource's title
        * file : a file object (ex. : file=open('test.pdf', rb))
        """
        id_ress = self.post_item("resources", data={"title": title}, file=file)
        return self.Ressource(self, id_ress)

    def get_ressources(self):
        """Get all ressources.
        Returns a list of Joplin.Ressource objects."""
        ressources_json = self.get_items("resources")
        return [self.get_ressource(r_j["id"]) for r_j in ressources_json]

    class Ressource:
        """
        A object to represent a Joplin Ressource.
        """

        def __init__(self, jop_api, id_ressource):
            """Get the ressource."""
            self.api = jop_api
            if id_ressource == "":
                raise Exception("Please provide the ressource's id.")
            self.id = id_ressource
            self.pull()

        def __setattr__(self, key, value, push=True):
            """Will only auto-push if Joplin.auto_push is True AND push is True."""
            self.__dict__[key] = value
            if push and self.api.auto_push and key in ressource_props:
                self.push()

        def delete(self):
            """Deletes the ressource."""
            self.api.delete_item("resources", self.id)

        def pull(self):
            """Pulls the ressource's update(s) from the Joplin API."""
            ressource_json = self.api.get_item("resources", self.id, ressource_props)
            for key in ressource_json.keys():  # set the attributes :
                self.__dict__[key] = ressource_json[key]

        def push(self):
            """Pushes the ressource update(s) to the Joplin API."""
            data = {}
            for key in ressource_props:
                data[key] = self.__dict__[key]

            self.api.put_item("resources", self.id, data)
            if self.api.verbose:
                print("Updated ressource", self.id)

        def get_notes(self):
            """Get a list of all notes associated with that ressource.
            Returns a list of Joplin.Note objects."""
            notes_json = self.api.get_items("resources", self.id, subitem_type="notes")
            return [self.api.get_note(n_j["id"]) for n_j in notes_json]

    def put_item(self, item_type, item_id, data):
        """Update a item (note, folder, etc.) using Joplin's REST API.
        Takes data as a dict (e.g. {"title":"New title"} to update the title)
        Ex.:
            * To update a note's title : put_item('notes','a1b2c3...', {'title':'New title'})
        """
        if type(data) != dict:
            raise TypeError("put_item only takes the data to update as a dict.")
        # Make base url :
        url = (
            "http://"
            + self.api_host
            + ":"
            + str(self.api_port)
            + "/"
            + item_type
            + "/"
            + item_id
        )
        # Append parameters :
        url += "?token=" + self.api_key

        if self.verbose:
            print("PUT ", url, "\nwith data :", data)
        req = requests.put(url, json.dumps(data))
        if self.verbose:
            print("HTTP", req.status_code)
        if req.status_code == 404:
            raise Exception("Item not found. Please check the id you provided.")
        if req.status_code != 200:
            if self.verbose:
                print(req.headers)
                print(req.text)
            raise Exception(
                "Could not connect to API. Please check that the host/port/key is correct."
            )
        return req.json()

    def post_item(
        self,
        item_type,
        data={
            "title": "Untitled",
            "parent_id": "",
            "source": "python_joplin",
            "source_application": "com.S73ph4n.python_joplin",
        },
        file=None,
        item_id="",
        subitem_type="",
    ):
        """Creates an item (note, folder, etc.) using Joplin's REST API.
        Ex.:
            * To create a note : put_item('notes')
        Returns the id of the new item.
        """
        # TODO : add removal of forbidden characters
        # Make base url :
        url = "http://" + self.api_host + ":" + str(self.api_port) + "/" + item_type
        if item_id != "":
            url += "/" + item_id
        if subitem_type != "":
            url += "/" + subitem_type
        # Append parameters :
        url += "?token=" + self.api_key

        if self.verbose:
            print("POST ", url, "\nwith data :", data)
        if item_type == "resources":
            # TODO : set the type of ressource
            req = requests.post(
                url, files=dict({"props": (None, json.dumps(data)), "data": file})
            )
        else:
            req = requests.post(url, json.dumps(data))
        if self.verbose:
            print("HTTP", req.status_code)
        if req.status_code == 404:
            raise Exception("Item not found. Please check the id you provided.")
        if req.status_code != 200:
            if self.verbose:
                print(req.headers)
                print(req.text)
            raise Exception(
                "Could not connect to API. Please check that the host/port/key is correct."
            )
        return req.json()["id"]

    def delete_item(self, item_type, item_id, subitem_type="", subitem_id=""):
        """Delete a item (note, folder, etc.) using Joplin's REST API.
        Ex.:
            * To delete a note : delete_item('notes','a1b2c3...')
        """
        # Make base url :
        url = (
            "http://"
            + self.api_host
            + ":"
            + str(self.api_port)
            + "/"
            + item_type
            + "/"
            + item_id
        )
        if subitem_type != "":
            url += "/" + subitem_type
        if subitem_id != "":
            url += "/" + subitem_id
        # Append parameters :
        url += "?token=" + self.api_key

        if self.verbose:
            print("DELETE ", url)
        req = requests.delete(url)
        if self.verbose:
            print("HTTP", req.status_code)
        if req.status_code == 404:
            raise Exception("Item not found. Please check the id you provided.")
        if req.status_code != 200:
            if self.verbose:
                print(req.headers)
                print(req.text)
            raise Exception(
                "Could not connect to API. Please check that the host/port/key is correct."
            )
        return req.text

    def search_item(self, search_string, item_type="", page=1):
        """
        N.B. : item_type should be singular (note/tag/folder/etc.)
        """
        # TODO : add removal of forbidden characters
        # Make base url :
        url = "http://" + self.api_host + ":" + str(self.api_port) + "/search"
        # Append parameters :
        url += "?query=" + search_string
        if item_type != "":
            url += "&type=" + item_type
        url += "&page=" + str(page)
        url += "&token=" + self.api_key

        if self.verbose:
            print("GET (search) ", url, "\nwith search string :", search_string)
        req = requests.get(url)
        if self.verbose:
            print("HTTP", req.status_code)
        if req.status_code == 404:
            raise Exception("Item not found. Please check the id you provided.")
        if req.status_code != 200:
            if self.verbose:
                print(req.headers)
                print(req.text)
            raise Exception(
                "Could not connect to API. Please check that the host/port/key is correct."
            )
        return req.json()

    def search_items(self, search_string, item_type=""):
        """
        Search for items using the Joplin API.
        """
        page_n, items = 0, []
        while page_n == 0 or page_json["has_more"] == "True":
            page_n += 1
            page_json = self.search_item(
                search_string, item_type=item_type, page=page_n
            )
            for item in page_json["items"]:
                items.append(item)
        return items
