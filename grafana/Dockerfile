FROM alpine:3.21 AS infinity-extractor

RUN apk add --no-cache unzip

COPY grafana/plugin-cache/infinity-plugin.zip /tmp/infinity.zip

RUN mkdir -p /plugins \
    && unzip -q /tmp/infinity.zip -d /plugins \
    && test -f /plugins/yesoreyeram-infinity-datasource/plugin.json

FROM grafana/grafana-oss:13.0.2

COPY --from=infinity-extractor \
    /plugins/yesoreyeram-infinity-datasource \
    /opt/grafana-plugins/yesoreyeram-infinity-datasource

ENV GF_PATHS_PLUGINS=/opt/grafana-plugins
