FROM python:3.13-slim-buster
WORKDIR /app
COPY requirements.txt .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
EXPOSE 8050
CMD ["uvicorn", "app.main.app", "--host","0.0.0.0","--port", "8050"]