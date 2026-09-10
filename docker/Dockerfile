# kinema_catalog viewer image.
#
# Built on top of the prebuilt osrf/ros desktop-full images, so a first run only
# pulls (fast) and adds a thin layer of description tooling on top.
#
#   docker build --build-arg ROS_DISTRO=lyrical -t kinema-catalog:lyrical docker/
#
# ROS 2 / Gazebo pairings (see https://gazebosim.org/docs/latest/ros_installation/):
#   lyrical (LTS, 2026) -> Jetty      rolling -> Jetty
#   kilted  (2025)      -> Ionic      jazzy (LTS, 2024) -> Harmonic
#   humble  (LTS, 2022) -> Fortress   iron (EOL) -> Fortress

ARG ROS_DISTRO=lyrical
FROM osrf/ros:${ROS_DISTRO}-desktop-full

ARG ROS_DISTRO
ENV ROS_DISTRO=${ROS_DISTRO}
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# Core description tooling. ros-gz is installed separately and allowed to fail:
# not every distro has a matching binary release, and rviz still works without it.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ros-${ROS_DISTRO}-xacro \
      ros-${ROS_DISTRO}-robot-state-publisher \
      ros-${ROS_DISTRO}-joint-state-publisher-gui \
      ros-${ROS_DISTRO}-rviz2 \
      python3-numpy \
      mesa-utils \
      libgl1-mesa-dri \
 && { apt-get install -y --no-install-recommends ros-${ROS_DISTRO}-ros-gz \
      || echo "WARNING: ros-gz has no binary release for ${ROS_DISTRO}; 'gz' viewer disabled"; } \
 && rm -rf /var/lib/apt/lists/*

# Qt/OpenGL defaults that behave under WSLg and plain X11 alike. QT_QPA_PLATFORM
# is pinned to xcb because RViz renders through Ogre/GLX: if Qt selects its
# wayland plugin (which it does whenever WAYLAND_DISPLAY is set, as under WSLg),
# the render window aborts with "Invalid parentWindowHandle (wrong server or
# screen)". The launcher passes the same value so existing images need no rebuild.
# QT_QUICK_BACKEND is deliberately NOT set. Forcing Qt Quick's software backend
# segfaults Gazebo: its GUI is QML, and the MinimalScene plugin embeds a real
# OpenGL item, so the software scenegraph tears the GL context down underneath it
# (crash in QOpenGLContext::doneCurrent — see issue #4). RViz is QWidgets and
# never touched Qt Quick, which is why only Gazebo was affected.
ENV QT_X11_NO_MITSHM=1 \
    QT_QPA_PLATFORM=xcb \
    RCUTILS_COLORIZED_OUTPUT=1

WORKDIR /catalog

# entrypoint.sh is deliberately NOT copied in. The launcher runs it from the
# mounted repo (/catalog/docker/entrypoint.sh), so the checked-out script is
# always what executes. Baking a copy in meant edits to the orchestrator were
# silently ignored until someone thought to rebuild the image — see issue #1.
CMD ["bash", "/catalog/docker/entrypoint.sh"]
