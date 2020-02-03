FROM python:3.7
RUN mkdir /api
WORKDIR /api
COPY ./requirements.txt /api/requirements.txt
RUN pip3 install -r /api/requirements.txt

CMD ["python3", "/api/src/app.py"]
