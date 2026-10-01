#!/bin/sh
# Maven and the JVM ignore the standard HTTP_PROXY / HTTPS_PROXY / NO_PROXY environment variables,
# which Docker injects into builds and containers when a proxy is configured (~/.docker/config.json
# "proxies", or --build-arg). This translates them:
#   proxy-from-env.sh maven-settings  -> a Maven settings.xml with <proxies> (build stage)
#   proxy-from-env.sh jvm-opts        -> -Dhttp(s).proxyHost/-Port/-nonProxyHosts flags (runtime)
# With no proxy variables set, it emits an empty settings.xml / nothing, so direct access still works.
set -eu

# "http://user:pass@host:3128/" -> host and port (credentials are not supported here).
parse() {
    hostport=${1#*://}
    hostport=${hostport%%/*}
    hostport=${hostport##*@}
    host=${hostport%:*}
    port=${hostport##*:}
    [ "$port" = "$hostport" ] && port=80
    printf '%s %s' "$host" "$port"
}

# "localhost,.corp.net,10.0.0.0/8" -> "localhost|*.corp.net" (JVM/Maven syntax; CIDR ranges dropped).
non_proxy_hosts() {
    printf '%s' "${NO_PROXY:-${no_proxy:-}}" | tr ',' '\n' | sed -e 's/^ *//' -e 's/ *$//' \
        | grep -v '/' | grep -v '^$' | sed -e 's/^\./*./' | paste -sd '|' -
}

HTTP_P=${HTTP_PROXY:-${http_proxy:-}}
HTTPS_P=${HTTPS_PROXY:-${https_proxy:-$HTTP_P}}
NON_PROXY=$(non_proxy_hosts || true)

case "${1:-}" in
    maven-settings)
        echo '<settings><proxies>'
        for entry in "http $HTTP_P" "https $HTTPS_P"; do
            protocol=${entry%% *}
            url=${entry#* }
            [ -z "$url" ] && continue
            set -- $(parse "$url")
            echo "  <proxy><id>env-$protocol</id><active>true</active><protocol>$protocol</protocol>"
            echo "    <host>$1</host><port>$2</port><nonProxyHosts>$NON_PROXY</nonProxyHosts></proxy>"
        done
        echo '</proxies></settings>'
        ;;
    jvm-opts)
        opts=""
        if [ -n "$HTTP_P" ]; then
            set -- $(parse "$HTTP_P")
            opts="$opts -Dhttp.proxyHost=$1 -Dhttp.proxyPort=$2"
        fi
        if [ -n "$HTTPS_P" ]; then
            set -- $(parse "$HTTPS_P")
            opts="$opts -Dhttps.proxyHost=$1 -Dhttps.proxyPort=$2"
        fi
        if [ -n "$opts" ] && [ -n "$NON_PROXY" ]; then
            opts="$opts -Dhttp.nonProxyHosts=$NON_PROXY"
        fi
        printf '%s' "$opts"
        ;;
    *)
        echo "usage: $0 maven-settings|jvm-opts" >&2
        exit 2
        ;;
esac
