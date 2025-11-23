# Use AWS Lambda Python base image for guaranteed compatibility
FROM public.ecr.aws/lambda/python:3.11

# Install FFmpeg compatible with GLIBC 2.26 (Amazon Linux 2 compatible)
RUN yum update -y && yum install -y tar xz && \
    curl -Lo ffmpeg-release.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz && \
    tar -xf ffmpeg-release.tar.xz && \
    mv ffmpeg-*-arm64-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-arm64-static/ffprobe /usr/local/bin/ && \
    chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe && \
    rm -rf ffmpeg* && \
    yum clean all && \
    ffmpeg -version

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