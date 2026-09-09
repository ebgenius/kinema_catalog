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

# Qt/OpenGL defaults that behave under WSLg and plain X11 alike.
ENV QT_X11_NO_MITSHM=1 \
    QT_QUICK_BACKEND=software \
    RCUTILS_COLORIZED_OUTPUT=1

COPY entrypoint.sh /usr/local/bin/kinema-entrypoint
RUN chmod +x /usr/local/bin/kinema-entrypoint

WORKDIR /catalog
ENTRYPOINT ["/usr/local/bin/kinema-entrypoint"]
