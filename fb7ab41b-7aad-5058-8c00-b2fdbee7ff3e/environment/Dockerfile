FROM rinzler-harbor-base:latest

COPY bundle /opt/rinzler-task/bundle

RUN rinzler harbor init-db --bundle /opt/rinzler-task/bundle --db /opt/rinzler-task/seed.db \
 && test -f /opt/rinzler-task/seed.db \
 && mkdir -p /work \
 && cp /opt/rinzler-task/seed.db /work/rinzler.db

ENV DATABASE_URL=sqlite:////work/rinzler.db
ENV YC_BENCH_EXPERIMENT=/opt/rinzler-task/bundle/config.toml

WORKDIR /work
