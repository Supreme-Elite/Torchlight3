FROM python:3.6

WORKDIR /home/torchlight

RUN apt update && apt install -y youtube-dl ffmpeg

## YOUTUBE-DL FIX
RUN wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl \
    && chmod a+rx /usr/local/bin/youtube-dl

ADD . /home/torchlight
RUN mv GeoLite2-City.mmdb /usr/share/GeoIP/
RUN pip3 install -r requirements.txt

# Clean
RUN rm -rf /home/torchlight/.git \
    && rm -rf /var/lib/apt/lists/*

CMD [ "python", "./main.py" ]