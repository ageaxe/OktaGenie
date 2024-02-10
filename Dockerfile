# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the desired file into the container
COPY /Users/apal2/.cache/lm-studio/models/TheBloke/phi-2-GGUF/phi-2.Q8_0.ggu .

# Copy the data directory into the container
COPY data ./data

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]