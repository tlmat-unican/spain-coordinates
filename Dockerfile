FROM python:3.6-alpine
LABEL authors="Jorge Lanza <jlanza@tlmat.unican.es>, Pablo Sotres <psotres@tlmat.unican.es>"

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN set -x \
  && apk add --no-cache --virtual .build-deps build-base \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-deps \
  && rm -Rf /root/* /root/.cache

COPY . /usr/src/app

# Expose the Flask port
EXPOSE 5000
CMD [ "python", "./app.py" ]
