FROM python:3.11.9-bullseye

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade --no-cache-dir -r requirements.txt 

COPY ./app .

CMD ["fastapi", "run", "/app/main.py", "--host", "0.0.0.0", "--port", "80"]