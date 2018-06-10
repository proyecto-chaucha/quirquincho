
FROM alpine:3.7

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools

RUN pip3 install python-telegram-bot bitcoin requests

WORKDIR /usr/src/quirquincho
COPY . /usr/src/quirquincho


CMD ["python3","."]
