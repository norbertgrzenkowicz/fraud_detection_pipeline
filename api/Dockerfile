FROM python:3.10


WORKDIR /code

RUN pip install --no-cache-dir --upgrade fastapi["standard"] pandas scikit-learn

COPY ./ /code/

CMD ["fastapi", "run", "api.py", "--port", "8100"]