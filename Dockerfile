FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usamos ENTRYPOINT para que possamos passar argumentos como "--test" diretamente no comando `docker run`.
ENTRYPOINT ["python", "main.py"]