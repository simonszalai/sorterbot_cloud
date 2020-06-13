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

# ARG AWS_PROFILE=default
ARG WEIGHTS_URL_ARG
ARG DEPLOY_REGION_ARG

ENV MODE=$MODE_ARG
ENV DEPLOY_REGION=$DEPLOY_REGION_ARG
ENV WEIGHTS_URL=$WEIGHTS_URL_ARG


# # Copy sample weigths, then overwrite them if WEIGHTS_URL is provided
# COPY ./weights/model_final.pth /sorterbot_cloud/weights/model_final.pth
# RUN if [ "$WEIGHTS_URL" != "" ] ; then \
#   # Install AWS CLI
#   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
#   unzip awscliv2.zip \
#   ./aws/install \
#   # Download weights from S3
#   --profile ${AWS_PROFILE} \
#   --mount=type=secret,id=aws_credentials,dst=/root/.aws/credentials \
#   --mount=type=secret,id=aws_config,dst=/root/.aws/config \
#   aws s3 cp ${WEIGHTS_URL} /sorterbot_cloud/weights/model_final.pth ; \
# fi ;

# RUN \
  # Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN aws s3 cp s3://sorterbot-weights-fbcggris/model_final.pth /sorterbot_cloud/weights/model_final.pth --region ${DEPLOY_REGION_ARG}
RUN echo ls
RUN ls /sorterbot_cloud/weights
RUN stat -f%z /sorterbot_cloud/weights/model_final.pth
  # Download weights from S3
  # --profile ${AWS_PROFILE} \
  # --mount=type=secret,id=aws_credentials,dst=/root/.aws/credentials \
  # --mount=type=secret,id=aws_config,dst=/root/.aws/config \
RUN echo WEIGHTS_URL: $WEIGHTS_URL
RUN echo WEIGHTS_URL_ARG: $WEIGHTS_URL_ARG

# Copy source code
COPY ./src /sorterbot_cloud/src
COPY ./tests /sorterbot_cloud/tests
COPY ./config.yaml /sorterbot_cloud/config.yaml
# COPY ./weights/model_final.pth /sorterbot_cloud/weights/model_final.pth

WORKDIR /sorterbot_cloud
ENV PYTHONUNBUFFERED 1

CMD ["python3", "/sorterbot_cloud/src/server.py"]
