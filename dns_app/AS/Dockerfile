FROM python:3.11-slim

WORKDIR /app

COPY server.py .
COPY database.txt .

EXPOSE 53533/udp

CMD ["python", "server.py"]