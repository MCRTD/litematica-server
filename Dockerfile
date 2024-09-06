FROM python:3.12-alpine
COPY requirements.txt /requirements.txt
RUN pip install  -r /requirements.txt
COPY static /app/static
COPY public /app/public
COPY main.py /app/main.py
WORKDIR /app
# ENV PORT 8080
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
