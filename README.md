# Python\_Joplin
A package to handle the Joplin API with Python. Relies on the [Joplin Data API](https://joplinapp.org/api/references/rest_api/)

WARNING : This is a work in progress. There will probably be a few breaking changes in the future, so please don't use it in production. This code comes without any warranties or support.

Additionnal tools can be found in the 'tools' directory.

# Installation
That's a bad idea.
But if you must :
```pip install git+https://github.com/S73ph4n/python_joplin```

To uninstall:
```pip uninstall python_joplin```

# Usage

Connecting to the API:

(Make sure Joplin is running and the Web Clipper API is active. You can find the API key in Joplin's options.)
```python
from python_joplin import Joplin
my_jop = Joplin(key='myJoplinToken1a2b3c4...') 
```

## Examples

Printing a list of all notes:
```python
note_list = my_jop.get_notes()
for note in note_list: print(note.title)
```

Printing a list of all notebooks:
```python
notebooks_list = my_jop.get_notebooks()
for notebook in notebooks_list: print(notebook.title)
```

Printing a list of all notes in a notebook:
```python
my_notebook = my_jop.get_notebooks()[0] #take the first notebook
print(my_notebook.title)
note_list = my_notebook.get_notes()
for note in note_list: print(note.title)
```

Reading a note's properties:
```python
my_note = my_jop.get_note('myNoteIDa1a2b3c4...')
print('Title:', my_note.title)
print('Body:', my_note.body)
print('Tags:')
for tag in my_note.tags: print(tag.title)
print('Ressources:')
for ressource in my_note.ressources: print(ressource.title)
```

Creating a note:
```python
my_note = my_jop.new_note()
my_note.title = 'My New Note'
my_note.body = 'The note\'s body'
```

Updating an existing note:
```python
my_note = my_jop.get_note('myNoteIDa1a2b3c4...')
my_note.body += 'The note\'s body'
```

Deleting a note:
```python
my_note = my_jop.get_note('myNoteIDa1a2b3c4...')
my_note.delete()
```

# Getting help
The code is documented, the ```help``` command should provide you with plenty of information:
```python
help(Joplin)
help(Joplin.Note)
help(Joplin.Tag)
help(Joplin.Notebook)
help(Joplin.Ressource)
```

# Contributing
Feel free to contribute. Pull requests welcome.
