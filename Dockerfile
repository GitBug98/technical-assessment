# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /code/

# Expose the port Uvicorn will run on
EXPOSE 8000

# Run Uvicorn ASGI server for handling HTTP and WebSockets
CMD ["uvicorn", "project.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
