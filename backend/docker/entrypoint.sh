#!/bin/sh
# Starts the backend with the container's proxy environment (if any) applied to the JVM, so the
# catalog importer and worldstate poller can reach Warframe's servers behind a proxy.
set -euf  # -f: no globbing, so a *.domain in the proxy flags stays literal
PROXY_OPTS=$(/app/proxy-from-env.sh jvm-opts)
# shellcheck disable=SC2086 # word splitting of the -D flags is intended
exec java $PROXY_OPTS ${JAVA_OPTS:-} -jar /app/app.jar "$@"
