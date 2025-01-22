FROM python:3.10


WORKDIR /code

RUN pip install --no-cache-dir --upgrade fastapi["standard"] pandas scikit-learn

COPY ./ /code/

# CMD ["ls", "/code/src"]

EXPOSE 8100

CMD ["fastapi", "run", "src/main.py", "--port", "8100"]
