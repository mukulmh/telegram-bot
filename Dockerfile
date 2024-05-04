# Use an official Python image as a base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

#RUN apk add postgresql-dev gcc musl-dev
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip setuptools wheel

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/