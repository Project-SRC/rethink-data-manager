FROM python:3-alpine

WORKDIR /app

RUN apk add --no-cache gcc libffi-dev musl-dev openssl-dev

COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src/ /app/

EXPOSE 8765 443

CMD python3 main.py
