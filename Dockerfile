FROM python:3.6-alpine
LABEL authors="Jorge Lanza <jlanza@tlmat.unican.es>, Pablo Sotres <psotres@tlmat.unican.es>"

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN set -x \
  && apk add --no-cache --virtual .build-deps build-base \
  && pip install --no-cache-dir gunicorn \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-deps \
  && rm -Rf /root/* /root/.cache

COPY . /usr/src/app

EXPOSE 5000
# Start with Flask
#CMD [ "python", "./app.py" ]
# Start with gunicorn
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]
