FROM python:3.7
RUN mkdir /sorterbot_cloud
COPY ./requirements.txt /sorterbot_cloud/requirements.txt
RUN pip3 install cython
RUN pip3 install -r /sorterbot_cloud/requirements.txt
RUN pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

RUN git clone https://github.com/facebookresearch/detectron2.git
WORKDIR /detectron2
RUN pip3 install -e .
COPY ./src/locator/config/faster_rcnn_R_50_FPN_3x.yaml /detectron2/configs/COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml

WORKDIR /sorterbot_cloud

CMD ["python3", "/sorterbot_cloud/src/api.py"]
