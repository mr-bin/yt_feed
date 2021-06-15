FROM ubuntu:20.04

WORKDIR /opt

RUN apt-get update && apt-get install -y \
		ca-certificates \
        make \
		g++ \
		gcc \
		libexpat1-dev \
		libssl-dev \
		zip \
		unzip \
        zlib1g-dev \
		python3 \
		python3-setuptools \
		python3-pip \
		python3-dev \
        libyaml-0-2 \
		build-essential \
		libsctp1 \
		libyaml-dev \
		libffi-dev \
	&& rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade setuptools==49.0

add ./etc /opt/etc
add ./src /opt/src
add ./buildout.cfg /opt
add ./versions.cfg /opt
add ./requirements.txt /opt

RUN pip install -r requirements.txt
RUN buildout

CMD ["/opt/bin/manage.py"]
