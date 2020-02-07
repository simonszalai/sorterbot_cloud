FROM python:3.7
RUN mkdir /sorterbot_cloud
COPY ./requirements.txt /sorterbot_cloud/requirements.txt
RUN pip3 install -r /sorterbot_cloud/requirements.txt

CMD ["python3", "/sorterbot_cloud/src/app.py"]
