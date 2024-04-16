FROM python:3.11-slim

WORKDIR /app

ADD . .

RUN pip install -r requirements.txt
EXPOSE 6069
#CMD ['python3', '-m', 'uvicorn' ,'main:app','--host', '0.0.0.0', '--port', '6061']
CMD python -m uvicorn main:app --host 0.0.0.0 --port 6069