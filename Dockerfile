# syntax=docker/dockerfile:experimental
FROM python:3.7

# Create directories
RUN mkdir /sorterbot_cloud
RUN mkdir /detectron_custom_weights

# Install Requirements
COPY ./requirements.txt /sorterbot_cloud/requirements.txt
RUN pip3 install -r /sorterbot_cloud/requirements.txt
RUN pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN pip3 install detectron2==0.1 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/index.html

# Download weights for vectorizer
RUN curl https://download.pytorch.org/models/resnet18-5c106cde.pth --output /root/.cache/torch/checkpoints/resnet18-5c106cde.pth --create-dirs

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws configure set region eu-central-1

# ARG DOWNLOAD_WEIGHTS
ARG AWS_PROFILE=default
ARG WEIGHTS_URL
ENV CUSTOM_WEIGHTS=$WEIGHTS_URL
ENV DISABLE_AWS=0

# Download custom trained weights for Detectron from s3
RUN if [ "$WEIGHTS_URL" != "" ] ; then --mount=type=secret,id=aws_credentials,dst=/root/.aws/credentials --profile ${AWS_PROFILE} --mount=type=secret,id=aws_config,dst=/root/.aws/config aws s3 cp ${WEIGHTS_URL} /sorterbot_cloud/weights/model_final.pth ; fi ;

# Copy source code
COPY ./src /sorterbot_cloud/src
COPY ./tests /sorterbot_cloud/tests
COPY ./config.yaml /sorterbot_cloud/config.yaml

WORKDIR /sorterbot_cloud
ENV PYTHONUNBUFFERED 1

CMD ["python3", "/sorterbot_cloud/src/api.py"]
