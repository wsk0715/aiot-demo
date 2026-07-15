#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$HOME"
PX4_DIR="${SCRIPT_DIR}/PX4-Autopilot"

echo "=== [1/3] Clone PX4-Autopilot ==="
if [ ! -d "${PX4_DIR}" ]; then
    git clone https://github.com/PX4/PX4-Autopilot.git "${PX4_DIR}" --recurse-submodules
else
    echo "Already cloned: ${PX4_DIR}"
fi

echo ""
echo "=== [2/3] Run ubuntu.sh (install deps) ==="
cd "${PX4_DIR}"
bash ./Tools/setup/ubuntu.sh --no-nuttx

echo ""
echo "=== [3/3] Build & run SITL + Gazebo (gz_x500) ==="
echo "Starting Gazebo + PX4 SITL. Press Ctrl+C to stop."
make px4_sitl gz_x500
