FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}

# Install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Run
CMD [ "lambda_handler.handler" ]
