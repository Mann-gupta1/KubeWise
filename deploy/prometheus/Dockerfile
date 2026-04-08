FROM prom/prometheus:v2.53.0

USER root
COPY prometheus.yml.template /etc/prometheus/prometheus.yml.template
COPY entrypoint.sh /entrypoint.sh
# Base image has user `nobody` but not necessarily `nogroup`; root-owned 755 is readable/executable by nobody.
RUN chmod 755 /entrypoint.sh /etc/prometheus/prometheus.yml.template

USER nobody
EXPOSE 9090

ENTRYPOINT ["/entrypoint.sh"]
