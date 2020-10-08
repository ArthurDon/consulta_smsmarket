FROM python:3.7.3-alpine
ENV APPLICATION_ROOT="/app"
WORKDIR $APPLICATION_ROOT

COPY requirements.txt ${APPLICATION_ROOT}

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . $APPLICATION_ROOT

CMD ["python", "main.py"]