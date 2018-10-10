FROM python:3.6-alpine

WORKDIR /fatbot

#these are for Pillow
RUN apk --no-cache add build-base python-dev jpeg-dev zlib-dev freetype-dev

RUN apk --no-cache add bash wget &&\
    wget -qO /usr/local/bin/wait-for-it \
    https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && \
    chmod +x /usr/local/bin/wait-for-it

# Copy in requirements.txt first so changing the source
# code doesn't require these steps to run again
COPY requirements.txt .

RUN pip install -U -r requirements.txt

COPY . .
