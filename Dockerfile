# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Copy the desired file into the container
COPY phi-2.Q8_0.gguf .

# Copy the data directory into the container
COPY data ./data

# Add the current directory contents into the container at /app
ADD . /app

ENV MY_BOT_TOKEN "YOUR_BOT_TOKEN"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Run main.py when the container launches
CMD ["python", "main_docker.py"]