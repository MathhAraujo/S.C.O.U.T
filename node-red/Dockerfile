FROM nodered/node-red:4.0

COPY --chown=node-red:node-red package.json /data/package.json
RUN cd /data && npm install --omit=dev --unsafe-perm --no-update-notifier --no-fund

COPY --chown=node-red:node-red flows.json /data/flows.json

WORKDIR /usr/src/node-red
