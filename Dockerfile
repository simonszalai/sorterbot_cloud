# syntax=docker/dockerfile:experimental
FROM python:3.7

# Create directories
RUN mkdir /sorterbot_cloud
RUN mkdir /detectron_custom_weights

# Install Requirements
COPY ./requirements.txt /sorterbot_cloud/requirements.txt
RUN pip3 install -r /sorterbot_cloud/requirements.txt
RUN pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN pip3 install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/index.html

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws configure set region eu-central-1

# Download weights for vectorizer
RUN curl https://download.pytorch.org/models/resnet18-5c106cde.pth --output /root/.cache/torch/checkpoints/resnet18-5c106cde.pth --create-dirs

# Download custom trained weights for Detectron from s3
RUN --mount=type=secret,id=aws_credentials,dst=/root/.aws/credentials aws s3 cp s3://sorterbot-weights/model_final2.pth /detectron_custom_weights/model_final.pth

# Copy source code
COPY ./src /sorterbot_cloud/src
COPY ./tests /sorterbot_cloud/tests
COPY ./config.yaml /sorterbot_cloud/config.yaml

WORKDIR /sorterbot_cloud

CMD ["python3", "/sorterbot_cloud/src/api.py"]
