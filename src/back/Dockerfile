FROM python:3.12-alpine

ENV PYTHONPATH="${PYTHONPATH}:/src"

WORKDIR /src
    
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir -p /src/resultados/internal

COPY . .
# COPY app.py app.py

# ENV FLASK_APP=app:app

RUN adduser --disabled-password --no-create-home appuser
RUN chown -R appuser:appuser /src
RUN chown -R appuser:appuser /src/resultados

RUN chmod -R u+rwx /src 
RUN chmod -R 775 /src/resultados


USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
