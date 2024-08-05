FROM python:3.12-alpine
  
WORKDIR /src
    
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
  
COPY src/ .

# -u to force stdout and stderr streams to be unbuffered
ENTRYPOINT python -u app.py