FROM python:3.6-alpine

WORKDIR /fatbot

# Copy in requirements.txt first so changing the source
# code doesn't require these steps to run again
COPY requirements.txt .
#these are for Pillow
RUN apk --no-cache add build-base python-dev jpeg-dev zlib-dev freetype-dev

RUN pip install -U -r requirements.txt

COPY . .

CMD python main.py
