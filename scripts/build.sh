# =============================================================================
# FILE PURPOSE:
# Automated compilation and packaging pipeline for NoBlankPrintPVM.
# Clones or references CPython source, applies C-level patches, compiles
# using optimized make flags (-j$(nproc)), and packages the SDK archive.
# Run via: `bash scripts/build.sh`
# =============================================================================

set -e

BUILD_DIR="${HOME}/pvm-noblankprint"
SRC_DIR="${BUILD_DIR}/cpython-src"
INSTALL_PREFIX="/opt/noblankprint-pvm"
ARCHIVE_NAME="noblankprint-pvm-sdk.tar.gz"

echo "=================================================="
echo "Starting NoBlankPrintPVM Build & Packaging"
echo "=================================================="

mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

if [ ! -d "${SRC_DIR}" ]; then
    echo "[1/4] Cloning CPython source..."
    git clone --depth 1 https://github.com/python/cpython.git "${SRC_DIR}"
else
    echo "[1/4] CPython source already present at ${SRC_DIR}"
fi

echo "[2/4] Applying NoBlankPrint patches..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/patch_cpython.py" "${SRC_DIR}"

echo "[3/4] Configuring and Compiling CPython..."
cd "${SRC_DIR}"
./configure --prefix="${INSTALL_PREFIX}" --enable-optimizations --with-lto
make -j"$(nproc)"
sudo make install

echo "[4/4] Creating SDK distribution archive..."
cd /opt
sudo tar -czf "${BUILD_DIR}/${ARCHIVE_NAME}" noblankprint-pvm/

echo "=================================================="
echo "Build complete! SDK archive generated at:"
echo "  ${BUILD_DIR}/${ARCHIVE_NAME}"
echo "=================================================="
