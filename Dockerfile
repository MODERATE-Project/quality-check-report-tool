FROM python:3.12-alpine
  
WORKDIR /src
    
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
  
COPY src/ .

ENV FLASK_APP=app:app

# -u to force stdout and stderr streams to be unbuffered
# CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["uvicorn", "app:asgi_app", "--host", "0.0.0.0", "--port", "5000"]
