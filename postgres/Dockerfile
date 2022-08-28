FROM postgres:14-alpine

RUN apk update \
    && apk add \
    build-base \
    clang \
    llvm

RUN wget https://github.com/eulerto/wal2json/archive/refs/tags/wal2json_2_4.tar.gz
RUN tar -zxf wal2json_2_4.tar.gz
WORKDIR wal2json-wal2json_2_4
RUN make
RUN make install
