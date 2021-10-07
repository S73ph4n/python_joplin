FROM python:3.6

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . /app

CMD [ "python", "joplimap.py" ]
