# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the codebase into the container
COPY . .

## Set the environment variable for Flask
#ENV FLASK_APP=app.py

## Expose the port
#EXPOSE ${PORT}

# Run the application
CMD ["python", "app.py"]