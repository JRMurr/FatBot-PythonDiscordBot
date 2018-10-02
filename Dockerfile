FROM python:3.6-alpine

WORKDIR /fatbot

# Copy in requirements.txt first so changing the source
# code doesn't require these steps to run again
COPY requirements.txt .
RUN pip install -U -r requirements.txt

COPY . .

CMD python main.py
