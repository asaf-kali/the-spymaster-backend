FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY layer_handler.py .
COPY the-spymaster-dev-1655224940/layer ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "layer_handler.handle" ]
