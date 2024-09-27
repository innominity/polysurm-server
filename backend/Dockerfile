FROM nrel/energyplus:24.1.0

WORKDIR /home/app/web/

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt install -y \
    gcc libjpeg-dev \
    libxslt-dev \
    libpq-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    build-essential \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    libmariadb-dev \
    libmariadb-dev-compat \
    gettext \
    openssh-client \
    flake8 \
    locales \
    python3 \
    python3-pip \
    libgfortran5

RUN mkdir static

RUN mkdir media

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache

COPY . ./

RUN ["chmod", "+x", "dev.sh"]