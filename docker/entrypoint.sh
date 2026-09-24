#!/bin/bash
source /home/smriprep/.bashrc

export PATH="/opt/freesurfer/fsfast/bin:${PATH}"
export LD_LIBRARY_PATH="/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export DEBIAN_FRONTEND=noninteractive

# ------------------------------------------------------------------
# Headless MNE/PyVista rendering
# ------------------------------------------------------------------

# Use VTK/PyVista off-screen rendering.
export PYVISTA_OFF_SCREEN=true
export PYVISTA_USE_PANEL=false

# Software OpenGL
export PYOPENGL_PLATFORM=osmesa
export LIBGL_ALWAYS_SOFTWARE=1

# Do NOT force Qt offscreen when using Xvfb
unset QT_QPA_PLATFORM

# MNE 3D backend
export MNE_3D_BACKEND=pyvistaqt

# Avoid multisampling on software rendering
export MNE_3D_OPTION_MULTI_SAMPLES=0

# ------------------------------------------------------------------
# Xvfb
# ------------------------------------------------------------------

rm -f /tmp/.X99-lock

Xvfb :99 \
    -screen 0 1920x1080x24 \
    -nolisten tcp \
    +extension GLX \
    +extension RANDR \
    2>/tmp/xvfb_err.log &

XVFB_PID=$!

export DISPLAY=:99

echo "Waiting for Xvfb..."
until xdpyinfo -display :99 >/dev/null 2>&1; do
    sleep 0.2
done

echo "Xvfb started:"
xdpyinfo -display :99 | head

# ------------------------------------------------------------------
# Run command
# ------------------------------------------------------------------

exec "$@"