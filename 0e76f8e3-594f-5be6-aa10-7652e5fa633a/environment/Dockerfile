FROM 426628337772.dkr.ecr.ap-south-1.amazonaws.com/rinzler/harbor-base:latest

COPY bundle /opt/rinzler/bundle

RUN rinzler world init --bundle-dir /opt/rinzler/bundle --db /opt/rinzler/seed.db \
 && test -f /opt/rinzler/seed.db \
 && mkdir -p /work \
 && cp /opt/rinzler/seed.db /work/rinzler.db

ENV DATABASE_URL=sqlite:////work/rinzler.db

WORKDIR /work
