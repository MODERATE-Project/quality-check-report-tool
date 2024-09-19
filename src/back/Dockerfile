FROM python:3.12-alpine
  
WORKDIR /src
    
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
  
# COPY src/ .
COPY app.py app.py

ENV FLASK_APP=app:app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
