#!/usr/bin/env bash
set -euo pipefail
image='mysql@sha256:a81d043930e51745522bd5c430961cf8286f0a23f0a9a2a6e0108f7ea71b0902'
name="${1:-nsy-study-mysql-local}"
options=(--rm)
if [[ "$name" == --production ]]; then
  name=nsy-study-mysql-production
  options=(--restart unless-stopped --label nsy.study.judge=production)
elif [[ "$name" == nsy-study-mysql-production ]]; then
  echo "Use --production for the website judge." >&2
  exit 2
fi
[[ "$name" =~ ^nsy-study-mysql-[a-zA-Z0-9-]+$ ]] || exit 2
if docker container inspect "$name" >/dev/null 2>&1; then
  metadata="$(docker inspect -f '{{index .Config.Labels "nsy.study.judge"}} {{.Config.Image}} {{.HostConfig.NetworkMode}} {{.HostConfig.RestartPolicy.Name}}' "$name")"
  if [[ "$name" != nsy-study-mysql-production || "$metadata" != "production $image none unless-stopped" ]]; then
    echo "An existing container uses $name. Check its configuration." >&2
    exit 1
  fi
  if [[ "$(docker inspect -f '{{.State.Running}}' "$name")" != true ]]; then
    docker start "$name" >/dev/null
  fi
else
  MYSQL_ROOT_PASSWORD="$(openssl rand -hex 24)" docker run --detach "${options[@]}" --name "$name" --network none --memory 1g --cpus 2 --pids-limit 128 \
    --tmpfs /var/lib/mysql:rw,size=650m --env MYSQL_ROOT_PASSWORD \
    "$image" --skip-networking --skip-log-bin --local-infile=OFF --secure-file-priv=NULL
fi
for ((attempt=0; attempt<90; attempt++)); do
  # The entrypoint briefly starts a different server to initialize the data directory.
  if docker exec "$name" sh -c 'test "$(cat /proc/1/comm)" = mysqld && MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --protocol=socket -uroot -e "SELECT 1"' >/dev/null 2>&1; then
    echo "MySQL ready. Set CODE_PRACTICE_MYSQL_CONTAINER=$name before starting the app."
    exit 0
  fi
  sleep 1
done
echo "MySQL did not start. Check its container status." >&2
exit 1
