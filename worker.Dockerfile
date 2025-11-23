# Use AWS Lambda Python base image for guaranteed compatibility
FROM public.ecr.aws/lambda/python:3.11

# Install tar, xz and FFmpeg using static build for ARM64
RUN yum update -y && yum install -y tar xz && \
    curl -Lo ffmpeg.tar.xz https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz && \
    tar -xf ffmpeg.tar.xz && \
    mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe /usr/local/bin/ && \
    chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe && \
    rm -rf ffmpeg* && \
    yum clean all

# -------------------------
# Python dependencies
# -------------------------
COPY requirements.txt  ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}

# -------------------------
# Application code
# -------------------------
COPY . ${LAMBDA_TASK_ROOT}

CMD ["message_broker.handler.lambda_handler"]