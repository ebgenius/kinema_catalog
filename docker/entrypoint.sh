#!/usr/bin/env bash
# Container-side orchestrator. Turns a manifest row into a running RViz or Gazebo
# session. Driven entirely by env vars set by kinema_catalog.sh on the host:
#
#   KINEMA_ROBOT   robot id from docker/robots.tsv
#   KINEMA_VIEWER  rviz | gz
#   KINEMA_EXPORT  1 to also write the flattened URDF to /catalog/out/<id>.urdf
#
# Any argument given is executed instead (used by --shell).
set -euo pipefail

CATALOG=/catalog
MANIFEST="$CATALOG/docker/robots.tsv"
GEN_DIR=/tmp/kinema
INDEX=/tmp/kinema_index

bold() { printf '\033[1m%s\033[0m\n' "$*" >&2; }
info() { printf '\033[36m==>\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }

# ROS's setup files reference unset variables, so -u has to come off around them.
set +u
# shellcheck disable=SC1090
source "/opt/ros/$ROS_DISTRO/setup.bash"
set -u

# ---------------------------------------------------------------------------
# Make every description package under src/ resolvable as a ROS package without
# building a workspace: a synthetic ament index of symlinks. This is what makes
# `$(find pkg)` in xacro and `package://pkg/...` mesh URIs work instantly.
# ---------------------------------------------------------------------------
build_index() {
  rm -rf "$INDEX"
  mkdir -p "$INDEX/share/ament_index/resource_index/packages"
  local pxml dir name count=0
  while IFS= read -r pxml; do
    dir=$(dirname "$pxml")
    name=$(sed -n 's:.*<name>[[:space:]]*\([^<[:space:]]*\)[[:space:]]*</name>.*:\1:p' "$pxml" | head -1)
    if [ -z "$name" ]; then continue; fi
    # first one wins, so a package is never shadowed by a nested copy
    if [ -e "$INDEX/share/$name" ]; then continue; fi
    ln -sfn "$dir" "$INDEX/share/$name"
    : > "$INDEX/share/ament_index/resource_index/packages/$name"
    count=$((count + 1))
  done < <(find "$CATALOG/src" -name package.xml -not -path '*/.git/*' 2>/dev/null | sort)
  info "indexed $count ROS packages from src/"
  export AMENT_PREFIX_PATH="$INDEX:${AMENT_PREFIX_PATH:-}"
  # Gazebo resolves package:// by searching these paths for a dir named <pkg>
  export GZ_SIM_RESOURCE_PATH="$INDEX/share:${GZ_SIM_RESOURCE_PATH:-}"
  export IGN_GAZEBO_RESOURCE_PATH="$INDEX/share:${IGN_GAZEBO_RESOURCE_PATH:-}"
}

# ---------------------------------------------------------------------------
# Manifest lookup
# ---------------------------------------------------------------------------
lookup() {
  local want="$1" id family sub type path args mesh label
  while IFS=$'\t' read -r id family sub type path args mesh label; do
    case "$id" in ''|\#*) continue ;; esac
    if [ "$id" = "$want" ]; then
      R_FAMILY=$family; R_SUB=$sub; R_TYPE=$type; R_PATH=$path
      R_ARGS=$args; R_MESH=$mesh; R_LABEL=$label
      return 0
    fi
  done < "$MANIFEST"
  return 1
}

# Root link = the one link that is never a child of a joint. Used as RViz's
# fixed frame, which differs per robot (base_link, base, trunk, world, ...).
root_link() {
  python3 - "$1" <<'PY'
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
links = {l.get('name') for l in root.findall('link')}
children = {j.find('child').get('link') for j in root.findall('joint') if j.find('child') is not None}
free = sorted(links - children)
print(free[0] if free else (sorted(links)[0] if links else 'base_link'))
PY
}

generate_urdf() {
  mkdir -p "$GEN_DIR"
  local out="$GEN_DIR/robot.urdf"
  local src="$CATALOG/$R_PATH"
  [ -f "$src" ] || die "entry point not found: $R_PATH (is the submodule cloned?)"

  if [ "$R_TYPE" = xacro ]; then
    info "xacro $R_PATH ${R_ARGS/-/}"
    # shellcheck disable=SC2086
    if [ "$R_ARGS" = "-" ]; then
      xacro "$src" -o "$out"
    else
      xacro "$src" $R_ARGS -o "$out"
    fi
  else
    info "urdf $R_PATH"
    cp "$src" "$out"
  fi

  # Some URDFs (SO-ARM100) reference meshes by relative path; rewrite those to
  # absolute file:// URIs. The [^":] class deliberately skips package:// etc.
  if [ "$R_MESH" != "-" ]; then
    info "rewriting relative mesh paths against $R_MESH"
    # restricted to <mesh> lines so plugin filenames ("libfoo.so") are never touched
    sed -i "/<mesh/ s|filename=\"\\([^\":]*\\)\"|filename=\"file://$CATALOG/$R_MESH/\\1\"|g" "$out"
  fi

  ROOT_LINK=$(root_link "$out")
  info "root link: $ROOT_LINK"

  if [ "${KINEMA_EXPORT:-0}" = "1" ]; then
    mkdir -p "$CATALOG/out"
    cp "$out" "$CATALOG/out/$KINEMA_ROBOT.urdf"
    info "exported out/$KINEMA_ROBOT.urdf"
  fi
  echo "$out"
}

# Flatten every robot in the manifest and report what breaks. One index build for
# the whole run, so this is cheap enough to use as a CI check on the manifest.
check_all() {
  local id family sub type path args mesh label pass=0 fail=0
  local -a failed=()
  while IFS=$'\t' read -r id family sub type path args mesh label; do
    case "$id" in ''|\#*) continue ;; esac
    if [ ! -e "$CATALOG/src/$sub/.git" ] && [ -z "$(ls -A "$CATALOG/src/$sub" 2>/dev/null)" ]; then
      printf '  %-14s \033[2mSKIP  submodule not cloned\033[0m\n' "$id"
      continue
    fi
    R_FAMILY=$family; R_SUB=$sub; R_TYPE=$type; R_PATH=$path
    R_ARGS=$args; R_MESH=$mesh; R_LABEL=$label
    KINEMA_ROBOT=$id
    if ( generate_urdf >/dev/null 2>&1 ); then
      printf '  %-14s \033[32mok\033[0m    %s\n' "$id" "$R_LABEL"
      pass=$((pass + 1))
    else
      printf '  %-14s \033[31mFAIL\033[0m  %s\n' "$id" "$R_LABEL"
      failed+=("$id")
      fail=$((fail + 1))
    fi
  done < "$MANIFEST"

  printf '\n%d ok, %d failed\n' "$pass" "$fail"
  if [ "$fail" -gt 0 ]; then
    printf 'failed: %s\n' "${failed[*]}"
    printf 'rerun one for the error:  ./kinema_catalog.sh %s --viewer none\n' "${failed[0]}"
    return 1
  fi
  return 0
}

PIDS=()
cleanup() {
  for p in "${PIDS[@]:-}"; do kill "$p" 2>/dev/null || true; done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

start_state_publishers() {
  local urdf="$1"
  ros2 run robot_state_publisher robot_state_publisher "$urdf" >/tmp/rsp.log 2>&1 &
  PIDS+=($!)
  ros2 run joint_state_publisher_gui joint_state_publisher_gui >/tmp/jsp.log 2>&1 &
  PIDS+=($!)
}

view_rviz() {
  local urdf="$1"
  local cfg=$GEN_DIR/robot.rviz
  sed "s|__FIXED_FRAME__|$ROOT_LINK|" "$CATALOG/docker/rviz/robot.rviz" > "$cfg"
  start_state_publishers "$urdf"
  info "launching rviz2 — close the window to stop"
  rviz2 -d "$cfg"
}

view_gz() {
  local urdf="$1"
  command -v gz >/dev/null 2>&1 || command -v ign >/dev/null 2>&1 \
    || die "Gazebo is not available in this image (no ros-gz for $ROS_DISTRO). Try --viewer rviz, or a different --distro."

  # Fortress-era ros_gz ships ign_gazebo.launch.py, Harmonic+ ships gz_sim.launch.py
  local share launch
  share=$(ros2 pkg prefix ros_gz_sim 2>/dev/null)/share/ros_gz_sim/launch
  if [ -f "$share/gz_sim.launch.py" ]; then launch=gz_sim.launch.py
  elif [ -f "$share/ign_gazebo.launch.py" ]; then launch=ign_gazebo.launch.py
  else die "ros_gz_sim launch files not found"; fi

  info "starting Gazebo ($launch)"
  ros2 launch ros_gz_sim "$launch" gz_args:="-r empty.sdf" >/tmp/gz.log 2>&1 &
  PIDS+=($!)
  start_state_publishers "$urdf"

  info "waiting for Gazebo to come up"
  local i
  for i in $(seq 1 30); do
    sleep 1
    if ros2 topic list 2>/dev/null | grep -q '/robot_description'; then break; fi
  done

  info "spawning $KINEMA_ROBOT"
  ros2 run ros_gz_sim create -topic robot_description -name "$KINEMA_ROBOT" -z 0.6 \
    || die "spawn failed — see /tmp/gz.log"
  info "spawned. close the Gazebo window to stop"
  wait -n "${PIDS[@]}" 2>/dev/null || true
}

# ---------------------------------------------------------------------------
main() {
  # --shell and friends: run whatever was asked, in a ROS-sourced environment
  if [ "$#" -gt 0 ]; then
    build_index
    exec "$@"
  fi

  [ -n "${KINEMA_ROBOT:-}" ] || die "KINEMA_ROBOT is not set"

  # manifest-wide check: flatten everything, report failures
  if [ "$KINEMA_ROBOT" = all ]; then
    bold "checking every robot in the manifest — ROS 2 $ROS_DISTRO"
    build_index
    check_all
    return $?
  fi

  lookup "$KINEMA_ROBOT" || die "unknown robot '$KINEMA_ROBOT' (see ./kinema_catalog.sh --list)"

  bold "$R_LABEL  [$R_FAMILY]  ROS 2 $ROS_DISTRO"
  build_index
  local urdf
  urdf=$(generate_urdf)

  case "${KINEMA_VIEWER:-rviz}" in
    rviz) view_rviz "$urdf" ;;
    gz)   view_gz "$urdf" ;;
    none) info "URDF generated at $urdf" ;;
    *)    die "unknown viewer '${KINEMA_VIEWER}'" ;;
  esac
}

main "$@"
