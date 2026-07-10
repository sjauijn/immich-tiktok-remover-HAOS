ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip jq

COPY immich_tiktok_remover /opt/immich_tiktok_remover/immich_tiktok_remover
COPY requirements.txt /opt/immich_tiktok_remover/requirements.txt

# stable-lite build: only filename/date heuristics, no easyocr/moviepy ML stack (~100MB vs ~4.1GB)
RUN pip install --no-cache-dir --break-system-packages -r /opt/immich_tiktok_remover/requirements.txt

ENV PYTHONPATH="/opt/immich_tiktok_remover"

COPY run.sh /
RUN chmod a+x /run.sh

LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="mxc2 (ported)" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="mxc2" \
    org.opencontainers.image.authors="mxc2" \
    org.opencontainers.image.url="https://github.com/mxc2/immich-tiktok-remover" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}

CMD [ "/run.sh" ]
