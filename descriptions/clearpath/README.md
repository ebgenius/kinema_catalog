# Clearpath platforms

`clearpath_common` ships each platform only as a xacro macro. A Clearpath robot's
description is generated from its `robot.yaml` by `clearpath_generator_common`, so
the fork has no file to open directly. Each file here is what that generator writes
for a `robot.yaml` that names only the platform: the `common` include, the platform
include, and the macro call. Attachments such as bumpers and top plates, sensors and
mounts are left out.
