# Use the official Python image as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port Gunicorn will run on
EXPOSE 8000

# Start the application with Gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "-w", "4", "-b", "0.0.0.0:8000"]
