# JoplICal.py
Sync your calendar with Joplin.

Looks for notes' dates and build a iCalendar file (.ics) from it.
The following dates are used:
* The due date (for todos)
* Any string 
Creates an event with the title as note's title and the description as the note's body.
## Usage
Install requirements:
```bash
pip install -r requirements.txt
```

Run the script:
```bash
python joplical.py
```

## With Docker (recommended)
```sh
docker build -t joplical https://github.com/S73ph4n/python_joplin.git\#:tools/joplical
docker run -it --network host -e JOPLIN_TOKEN="myJoplinToken1a2b3c..." -v ./joplical_files:/data joplical
```

or with docker-compose :

```yaml
services:
  joplimap:
    build: ~/src/python_joplin/tools/joplimap
    environment:
      - JOPLIN_TOKEN=myJoplinToken1a2b3c...
    volumes:
      - ./joplical_files:/data
    network_mode: host
```

## Configuration
All the variables which this script asks for (JOPLIN\_TOKEN) can be set from environment variables.
