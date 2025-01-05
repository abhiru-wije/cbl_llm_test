# Use an official Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /main

# Copy the application files into the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Flask app will use
EXPOSE 5003

# Command to run the Flask app
CMD ["python", "main.py"]
