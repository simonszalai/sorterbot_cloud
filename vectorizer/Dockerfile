FROM python:3.7
RUN mkdir /vectorizer
WORKDIR /vectorizer
COPY ./requirements.txt /vectorizer/requirements.txt
RUN pip3 install -r /vectorizer/requirements.txt

CMD ["python3", "/vectorizer/src/vectorizer.py"]
