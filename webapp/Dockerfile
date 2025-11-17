FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug"]
