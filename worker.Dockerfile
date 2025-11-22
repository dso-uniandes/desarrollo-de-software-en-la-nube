# Use your custom FFmpeg image as base
FROM jehernandezr/python_313_ffmpeg:latest

# Install AWS Lambda Runtime Interface Client
RUN pip install awslambdaric

# Install curl and AWS Lambda Runtime Interface Emulator
RUN apt-get update && apt-get install -y curl && \
    curl -Lo /usr/local/bin/aws-lambda-rie https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie && \
    chmod +x /usr/local/bin/aws-lambda-rie && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Set Lambda environment variables
ENV LAMBDA_TASK_ROOT=/app
ENV LAMBDA_RUNTIME_DIR=/app

# Expose port 8080 (Lambda uses this port in container mode)
EXPOSE 8080

# Create entrypoint script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then' >> /entrypoint.sh && \
    echo '    exec /usr/local/bin/aws-lambda-rie python -m awslambdaric $1' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '    exec python -m awslambdaric $1' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set entrypoint and default handler
ENTRYPOINT ["/entrypoint.sh"]
CMD ["message_broker.worker.lambda_handler"]







