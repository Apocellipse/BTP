# Use an official Python runtime as a parent image
FROM ubuntu:22.04

# Set the working directory in the container
WORKDIR /prot1_serv
RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip install uvicorn

# Copy the current directory contents into the container at /app
COPY . .
# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run myapp.py when the container launches
CMD ["uvicorn", "prot1_serv:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]