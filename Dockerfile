FROM python:3.8-slim

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy project
COPY src/ .
COPY Makefile .
COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y make
RUN make install-run

CMD ["make", "run"]
