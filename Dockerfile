FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app/


RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
# user to run out our process
# for security purpose
# otherwise app will run in root
RUN adduser -D user
# sets the ownership of all dirs within vol to our custom user
# -R is recursive
RUN chown -R user:user /vol/
# user can do everything so the owner can do everything with the dir
# rest can read and execute from dir
RUN chmod -R 755 /vol/web
USER user