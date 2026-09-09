#!/usr/bin/env bash
# kinema_catalog — browse and visualise every robot description in this catalog.
#
#   ./kinema_catalog.sh                     pick a robot interactively
#   ./kinema_catalog.sh --list              list everything
#   ./kinema_catalog.sh ur5e                open UR5e in RViz
#   ./kinema_catalog.sh go2 -v gz           open Unitree Go2 in Gazebo
#   ./kinema_catalog.sh fr3 -d humble       fall back to an older ROS 2 distro
#
# Works on native Linux and inside WSL2 (GUI via WSLg). Windows users: run
# kinema_catalog.ps1, which forwards into WSL.
set -euo pipefail

# --------------------------------------------------------------------------- config
DEFAULT_DISTRO=lyrical           # latest ROS 2 LTS (May 2026, Ubuntu 26.04)
DEFAULT_VIEWER=rviz
IMAGE_PREFIX=kinema-catalog

# Gazebo release paired with each ROS 2 distro (gazebosim.org/docs/latest/ros_installation)
gazebo_for() {
  case "$1" in
    lyrical|rolling) echo "Jetty"   ;;
    kilted)          echo "Ionic"   ;;
    jazzy)           echo "Harmonic";;
    humble|iron)     echo "Fortress";;
    *)               echo "unknown" ;;
  esac
}

SCRIPT=$(readlink -f "${BASH_SOURCE[0]}")
REPO_ROOT=$(dirname "$SCRIPT")
MANIFEST="$REPO_ROOT/docker/robots.tsv"

# --------------------------------------------------------------------------- output
if [ -t 1 ]; then
  B=$'\033[1m'; DIM=$'\033[2m'; R=$'\033[31m'; G=$'\033[32m'; C=$'\033[36m'; Y=$'\033[33m'; N=$'\033[0m'
else
  B=''; DIM=''; R=''; G=''; C=''; Y=''; N=''
fi
info() { printf '%s==>%s %s\n' "$C" "$N" "$*"; }
warn() { printf '%swarning:%s %s\n' "$Y" "$N" "$*" >&2; }
die()  { printf '%serror:%s %s\n' "$R" "$N" "$*" >&2; exit 1; }

usage() {
  cat <<EOF
${B}kinema_catalog${N} — visualise the robot descriptions in this catalog

${B}usage${N}
  ./kinema_catalog.sh [robot] [options]

${B}options${N}
  -v, --viewer <rviz|gz>   viewer to launch                (default: $DEFAULT_VIEWER)
  -d, --distro <distro>    ROS 2 distro                    (default: $DEFAULT_DISTRO)
                           lyrical | kilted | jazzy | humble | rolling
  -l, --list               list all robots and exit
      --export             also write the flattened URDF to out/<robot>.urdf
      --build              rebuild the docker image before running
      --no-cache           rebuild from scratch (implies --build)
      --shell              drop into a ROS shell in the container instead
      --gpu                pass through GPUs (--gpus all)
      --software-gl        force software OpenGL (fixes some WSL/VM setups)
  -h, --help               this message

${B}examples${N}
  ./kinema_catalog.sh                  interactive picker
  ./kinema_catalog.sh ur5e             UR5e in RViz on ROS 2 $DEFAULT_DISTRO
  ./kinema_catalog.sh go2 -v gz        Unitree Go2 in Gazebo $(gazebo_for "$DEFAULT_DISTRO")
  ./kinema_catalog.sh spot -d jazzy    Spot on ROS 2 jazzy / Gazebo Harmonic
EOF
}

# --------------------------------------------------------------------------- manifest
declare -a IDS FAMILIES SUBS LABELS
load_manifest() {
  [ -f "$MANIFEST" ] || die "manifest not found: $MANIFEST"
  local id family sub type path args mesh label
  while IFS=$'\t' read -r id family sub type path args mesh label; do
    case "$id" in ''|\#*) continue ;; esac
    IDS+=("$id"); FAMILIES+=("$family"); SUBS+=("$sub"); LABELS+=("$label")
  done < "$MANIFEST"
  [ "${#IDS[@]}" -gt 0 ] || die "no robots found in manifest"
}

index_of() {
  local want="$1" i
  for i in "${!IDS[@]}"; do [ "${IDS[$i]}" = "$want" ] && { echo "$i"; return 0; }; done
  return 1
}

# marks robots whose submodule is already on disk
cloned_mark() {
  if [ -n "$(ls -A "$REPO_ROOT/src/$1" 2>/dev/null)" ]; then printf '%s*%s' "$G" "$N"; else printf ' '; fi
}

list_robots() {
  local fam f i shown
  printf '%s%s robots — %s* %salready cloned\n\n' "$B" "${#IDS[@]}" "$G$N" "$DIM$N"
  for fam in arm mobile legged; do
    case "$fam" in
      arm)    f="arms / manipulators" ;;
      mobile) f="mobile bases" ;;
      legged) f="legged" ;;
    esac
    printf '%s%s%s\n' "$B" "$f" "$N"
    shown=0
    for i in "${!IDS[@]}"; do
      [ "${FAMILIES[$i]}" = "$fam" ] || continue
      printf '  %s %-14s %s%-34s%s %s%s%s\n' \
        "$(cloned_mark "${SUBS[$i]}")" "${IDS[$i]}" "" "${LABELS[$i]}" "" "$DIM" "${SUBS[$i]}" "$N"
      shown=$((shown + 1))
    done
    if [ "$shown" -eq 0 ]; then printf '  %s(none)%s\n' "$DIM" "$N"; fi
    printf '\n'
  done
}

pick_robot() {
  # fzf when available, otherwise a numbered menu — both write the id to stdout
  local i choice
  if command -v fzf >/dev/null 2>&1; then
    local sel
    sel=$(for i in "${!IDS[@]}"; do
            printf '%-14s %-34s %s\n' "${IDS[$i]}" "${LABELS[$i]}" "${FAMILIES[$i]}"
          done | fzf --height=60% --reverse --prompt='robot> ' --header='select a robot description')
    [ -n "$sel" ] || die "nothing selected"
    echo "${sel%% *}"
    return
  fi

  {
    printf '\n%sSelect a robot%s\n\n' "$B" "$N"
    for i in "${!IDS[@]}"; do
      printf '  %s%3d%s) %s %-14s %-34s %s%s%s\n' \
        "$C" "$((i + 1))" "$N" "$(cloned_mark "${SUBS[$i]}")" \
        "${IDS[$i]}" "${LABELS[$i]}" "$DIM" "${FAMILIES[$i]}" "$N"
    done
    printf '\n'
  } >&2
  read -r -p "number or id: " choice </dev/tty
  [ -n "$choice" ] || die "nothing selected"
  if [[ "$choice" =~ ^[0-9]+$ ]]; then
    [ "$choice" -ge 1 ] && [ "$choice" -le "${#IDS[@]}" ] || die "out of range: $choice"
    echo "${IDS[$((choice - 1))]}"
  else
    index_of "$choice" >/dev/null || die "unknown robot: $choice"
    echo "$choice"
  fi
}

pick_viewer() {
  local choice
  {
    printf '\n%sViewer%s\n\n' "$B" "$N"
    printf '  %s1%s) rviz  %s— robot model + joint sliders (fast, no physics)%s\n' "$C" "$N" "$DIM" "$N"
    printf '  %s2%s) gz    %s— Gazebo %s (physics, sensors)%s\n\n' "$C" "$N" "$DIM" "$(gazebo_for "$DISTRO")" "$N"
  } >&2
  read -r -p "viewer [1]: " choice </dev/tty
  case "${choice:-1}" in
    1|rviz) echo rviz ;;
    2|gz)   echo gz ;;
    *)      die "unknown viewer: $choice" ;;
  esac
}

# --------------------------------------------------------------------------- docker
require_docker() {
  command -v docker >/dev/null 2>&1 \
    || die "docker not found.$([ "$IS_WSL" = 1 ] && printf ' In WSL, enable Docker Desktop -> Settings -> Resources -> WSL integration for this distro.')"
  docker info >/dev/null 2>&1 \
    || die "the docker daemon is not reachable — is Docker Desktop running?"
}

ensure_image() {
  local image="$1"
  if [ "$FORCE_BUILD" = 0 ] && docker image inspect "$image" >/dev/null 2>&1; then
    return
  fi
  info "building $image (first run pulls osrf/ros:${DISTRO}-desktop-full, ~3 GB)"
  local args=(build --build-arg "ROS_DISTRO=$DISTRO" -t "$image" "$REPO_ROOT/docker")
  if [ "$NO_CACHE" = 1 ]; then args+=(--no-cache); fi
  docker "${args[@]}" || die "image build failed"
}

ensure_submodule() {
  local sub="$1"
  if [ -n "$(ls -A "$REPO_ROOT/src/$sub" 2>/dev/null)" ]; then return 0; fi
  command -v git >/dev/null 2>&1 || die "git not found, cannot clone src/$sub"
  info "cloning submodule src/$sub"
  git -C "$REPO_ROOT" submodule update --init -- "src/$sub" \
    || die "failed to clone src/$sub"
}

# WSLg or plain X11 — both end up as a list of docker args
display_args() {
  local -n out=$1
  if [ "$IS_WSL" = 1 ] && [ -d /mnt/wslg ]; then
    out=(-e "DISPLAY=${DISPLAY:-:0}"
         -e "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-wayland-0}"
         -e "XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir"
         -e "PULSE_SERVER=${PULSE_SERVER:-/mnt/wslg/PulseServer}"
         -v /tmp/.X11-unix:/tmp/.X11-unix
         -v /mnt/wslg:/mnt/wslg)
  else
    [ -n "${DISPLAY:-}" ] || die "DISPLAY is not set — no X server to draw on"
    if command -v xhost >/dev/null 2>&1; then
      xhost +local:root >/dev/null 2>&1 || warn "xhost failed; the GUI may not appear"
      XHOST_GRANTED=1
    fi
    out=(-e "DISPLAY=$DISPLAY"
         -v /tmp/.X11-unix:/tmp/.X11-unix)
  fi
  if [ "$SOFTWARE_GL" = 1 ]; then out+=(-e LIBGL_ALWAYS_SOFTWARE=1); fi
  if [ "$USE_GPU" = 1 ]; then out+=(--gpus all); fi
  return 0
}

# --------------------------------------------------------------------------- args
ROBOT=""; VIEWER=""; DISTRO="$DEFAULT_DISTRO"
FORCE_BUILD=0; NO_CACHE=0; DO_SHELL=0; DO_EXPORT=0; USE_GPU=0; SOFTWARE_GL=0
XHOST_GRANTED=0
DO_LIST=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    -v|--viewer)   VIEWER="${2:-}"; shift 2 ;;
    -d|--distro)   DISTRO="${2:-}"; shift 2 ;;
    -l|--list)     DO_LIST=1; shift ;;
    --export)      DO_EXPORT=1; shift ;;
    --build)       FORCE_BUILD=1; shift ;;
    --no-cache)    NO_CACHE=1; FORCE_BUILD=1; shift ;;
    --shell)       DO_SHELL=1; shift ;;
    --gpu)         USE_GPU=1; shift ;;
    --software-gl) SOFTWARE_GL=1; shift ;;
    -h|--help)     usage; exit 0 ;;
    -*)            die "unknown option: $1 (try --help)" ;;
    *)             [ -z "$ROBOT" ] || die "unexpected argument: $1"; ROBOT="$1"; shift ;;
  esac
done

case "$DISTRO" in
  lyrical|kilted|jazzy|humble|iron|rolling) ;;
  *) die "unsupported distro '$DISTRO' (lyrical, kilted, jazzy, humble, iron, rolling)" ;;
esac

IS_WSL=0
if grep -qi microsoft /proc/version 2>/dev/null; then IS_WSL=1; fi

load_manifest

if [ "$DO_LIST" = 1 ]; then list_robots; exit 0; fi

# --------------------------------------------------------------------------- run
IMAGE="$IMAGE_PREFIX:$DISTRO"

if [ "$DO_SHELL" = 1 ]; then
  require_docker
  ensure_image "$IMAGE"
  declare -a DISP; display_args DISP
  info "ROS 2 $DISTRO shell — the catalog is mounted at /catalog"
  exec docker run --rm -it "${DISP[@]}" -v "$REPO_ROOT:/catalog" "$IMAGE" bash
fi

[ -n "$ROBOT" ] || ROBOT=$(pick_robot)
idx=$(index_of "$ROBOT") || die "unknown robot '$ROBOT' — try ./kinema_catalog.sh --list"
[ -n "$VIEWER" ] || VIEWER=$(pick_viewer)
case "$VIEWER" in rviz|gz|none) ;; *) die "unknown viewer '$VIEWER' (rviz or gz)" ;; esac

printf '\n%s%s%s  %s·%s %s  %s·%s ROS 2 %s%s\n' \
  "$B" "${LABELS[$idx]}" "$N" "$DIM" "$N" "$VIEWER" "$DIM" "$N" "$DISTRO" \
  "$([ "$VIEWER" = gz ] && printf ' / Gazebo %s' "$(gazebo_for "$DISTRO")")"
printf '%ssrc/%s%s\n\n' "$DIM" "${SUBS[$idx]}" "$N"

require_docker
ensure_submodule "${SUBS[$idx]}"
ensure_image "$IMAGE"

declare -a DISP; display_args DISP
cleanup() { [ "$XHOST_GRANTED" = 1 ] && xhost -local:root >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run --rm -it \
  "${DISP[@]}" \
  -v "$REPO_ROOT:/catalog" \
  -e "KINEMA_ROBOT=$ROBOT" \
  -e "KINEMA_VIEWER=$VIEWER" \
  -e "KINEMA_EXPORT=$DO_EXPORT" \
  "$IMAGE"
