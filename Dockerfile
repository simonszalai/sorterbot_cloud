FROM python:3.7
RUN mkdir /sorterbot_cloud

COPY ./requirements.txt /sorterbot_cloud/requirements.txt
RUN pip3 install -r /sorterbot_cloud/requirements.txt
RUN pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN pip3 install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/index.html

COPY ./src /sorterbot_cloud/src
COPY ./tests /sorterbot_cloud/tests
COPY ./config.yaml /sorterbot_cloud/config.yaml

WORKDIR /sorterbot_cloud

CMD ["python3", "/sorterbot_cloud/src/api.py"]
