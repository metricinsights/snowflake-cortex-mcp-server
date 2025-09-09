FROM python:3.13.7-slim-bookworm
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install supervisor  # works only for unix systems
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY supervisord.conf /etc/supervisord.conf
RUN ln -s /usr/local/bin/supervisorctl /usr/local/bin/ctl # handy alias to use 'ctl' instead of 'supervisorctl'
CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]