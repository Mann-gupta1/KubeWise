FROM prom/prometheus:v2.53.0

USER root
COPY prometheus.yml.template /etc/prometheus/prometheus.yml.template
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown nobody:nogroup /entrypoint.sh /etc/prometheus/prometheus.yml.template

USER nobody
EXPOSE 9090

ENTRYPOINT ["/entrypoint.sh"]
