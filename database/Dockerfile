FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .
RUN python -m pip install --upgrade --no-cache-dir -r requirements.txt

COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY sf-class2-root.crt ${LAMBDA_TASK_ROOT}/sf-class2-root.crt

CMD ["lambda_function.lambda_handler"]
