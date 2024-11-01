ARG SRC_IMAGE
ARG SRC_TAG

FROM ${SRC_IMAGE}:${SRC_TAG}

RUN pip install --upgrade pip

WORKDIR /tmp/build
# Copy dependencies
COPY requirements.lock .
# Install dependencies
RUN pip install --no-deps --target ${LAMBDA_TASK_ROOT} -r requirements.lock

# Install local wheels
COPY wheels/ wheels/
RUN pip install --no-deps wheels/* --target ${LAMBDA_TASK_ROOT}

WORKDIR ${LAMBDA_TASK_ROOT}
# Copy source code
COPY service/ .
# Point to lambda handler
CMD [ "lambda_handler.handle"]
