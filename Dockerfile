FROM jehernandezr/python_313_ffmpeg:latest
COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

