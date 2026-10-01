FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY server.py .

EXPOSE 9090

CMD ["python", "server.py"]