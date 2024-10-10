# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the codebase into the container
COPY . .

# Set the environment variables for Flask
# The port variable is necessary for Heroku deployment
ENV FLASK_APP=app
ENV PORT=5000

# Expose the port
#EXPOSE 5000

# Run the application with gunicorn
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:$PORT app:$FLASK_APP"]