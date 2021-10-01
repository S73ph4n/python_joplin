# Python\_Joplin
A package to handle the Joplin API with Python. Relies on the [Joplin Data API](https://joplinapp.org/api/references/rest_api/)

WARNING : This is a work in progress. There will probably be a few breaking changes in the future, so please don't use it in production. This code comes without any warranties or support.

# Installation
That's a bad idea.
But if you must :
```pip install git+https://github.com/S73ph4n/python_joplin```

# Usage

Connecting to the API:
(Make sure Joplin is running and the Web Clipper API is active. You can find the API key in Joplin's options.)
```python
from python_joplin import python_joplin
my_jop = python_joplin.Joplin(key='myJoplinToken1a2b3c4...') 
```

## Examples

Reading a note's properties:
```python
my_note = my_jop.get_note('myNoteIDa1a2b3c4...')
print('Title:', my_note.title)
print('Body:', my_note.body)
print('Tags:')
for tag in my_note.tags:
	print(tag.title)
print('Ressources:')
for ressource in my_note.ressources:
	print(ressource.title)
```

Creating a note:
```python
my_note = my_jop.new_note()
my_note.title = 'My New Note'
my_note.body = 'The note\'s body'
my_note.push() #Push your updates to Joplin
```

Updating an existing note:
```python
my_note = my_jop.get_note('myNoteIDa1a2b3c4...')
my_note.body += 'The note\'s body'
my_note.push() #Push your updates to Joplin
```

Deleting a note:
```python
my_note = my_jop.get_note('myNoteIDa1a2b3c4...')
my_note.delete()'
```

# Getting help
The code is documented, the ```help``` command should provide you with plenty of information:
```python
help(python_joplin.Joplin)
help(python_joplin.Joplin.Note)
help(python_joplin.Joplin.Tag)
help(python_joplin.Joplin.Notebook)
help(python_joplin.Joplin.Ressource)
```

# Contributing
Feel free to contribute. Pull requests welcome.
