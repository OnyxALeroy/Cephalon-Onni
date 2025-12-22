FROM postgres:15

ENV AGE_VERSION=PG15/v1.6.0-rc0

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-15 \
    flex \
    bison \
    && git clone https://github.com/apache/age.git \
    && cd age \
    && git checkout ${AGE_VERSION} \
    && make install \
    && apt-get remove -y git build-essential flex bison \
    && apt-get autoremove -y \
    && apt-get clean

# Ensure AGE can be loaded
RUN echo "shared_preload_libraries = 'age'" >> /usr/share/postgresql/postgresql.conf.sample
