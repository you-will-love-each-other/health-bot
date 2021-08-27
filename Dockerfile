FROM python:3.9-slim

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false

# Create the working directory
WORKDIR /bot

# Copy the requirements into the container, and install deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code in last to optimize rebuilding the image
COPY . .

ENTRYPOINT ["python3"]
CMD ["bot.py"]
