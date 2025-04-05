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


# Expose the port Gunicorn will run on
EXPOSE 8000

# Start the application with Gunicor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

