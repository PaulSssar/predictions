<<<<<<< HEAD
FROM python:3.12-slim

RUN mkdir /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . /app

WORKDIR /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose gunicorn port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "predictions.wsgi:application"]
=======
FROM python:3.12-slim

RUN mkdir /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . /app

WORKDIR /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose gunicorn port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "predictions.wsgi:application"]
>>>>>>> 235e838110e4665b69016b4322617eccf9d9eff6
