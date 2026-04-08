#!/bin/sh
set -e
PORT="${PORT:-9090}"
TARGET="127.0.0.1:${PORT}"
sed "s|__SCRAPE_TARGET__|${TARGET}|g" /etc/prometheus/prometheus.yml.template > /tmp/prometheus.yml
exec /bin/prometheus \
  --config.file=/tmp/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --web.listen-address="0.0.0.0:${PORT}"
