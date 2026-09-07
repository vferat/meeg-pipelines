#!/bin/bash
source /home/smriprep/.bashrc


export PATH="/opt/freesurfer/fsfast/bin:${PATH}"
export LD_LIBRARY_PATH="/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export DEBIAN_FRONTEND=noninteractive

# 3D rendering settings
export MNE_3D_BACKEND=pyvistaqt
export QT_QPA_PLATFORM=offscreen
export MNE_3D_OPTION_MULTI_SAMPLES=1
export PYVISTA_OFF_SCREEN=true
export PYOPENGL_PLATFORM=osmesa
export LIBGL_ALWAYS_SOFTWARE=1

# Create a virtual display for 3D rendering
rm -f /tmp/.X99-lock
Xvfb :99 -screen 0 1024x768x24 -nolisten tcp 2>/tmp/xvfb_err.log &
XVFB_PID=$!
export DISPLAY=:99

echo "Waiting for Xvfb to start..."
until xdpyinfo >/dev/null 2>&1; do
    sleep 0.2
done

# Run command
exec "$@"