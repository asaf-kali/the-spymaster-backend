FROM python:3.8-slim

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy project
ADD api ./api
ADD templates ./templates
ADD the_spymaster ./the_spymaster
COPY Makefile .
COPY manage.py .
COPY pyproject.toml .
COPY requirements.txt .
COPY settings.toml .

# Install dependencies
RUN apt-get update && apt-get install -y make
RUN make install-run

CMD ["make", "run"]
