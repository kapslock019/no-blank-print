# =============================================================================
# FILE PURPOSE:
# System installation script deploying NoBlankPrintPVM runtime SDK into /opt
# and configuring the global symlink `/usr/local/bin/noblankprint-python`.
# Run via: `bash scripts/install.sh` or `sudo bash scripts/install.sh`
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_CANDIDATES=(
    "${SCRIPT_DIR}/noblankprint-pvm-sdk.tar.gz"
    "${SCRIPT_DIR}/../noblankprint-pvm-sdk.tar.gz"
    "${HOME}/pvm-noblankprint/noblankprint-pvm-sdk.tar.gz"
)

ARCHIVE=""
for cand in "${ARCHIVE_CANDIDATES[@]}"; do
    if [ -f "${cand}" ]; then
        ARCHIVE="${cand}"
        break
    fi
done

echo "=== Installing NoBlankPrintPVM SDK ==="
if [ -z "${ARCHIVE}" ]; then
    echo "Error: SDK archive noblankprint-pvm-sdk.tar.gz not found!"
    echo "Please build the SDK first using scripts/build.sh"
    exit 1
fi

echo "[1/3] Extracting ${ARCHIVE} into /opt/..."
sudo mkdir -p /opt
sudo tar -xzf "${ARCHIVE}" -C /opt

echo "[2/3] Linking python binary to /usr/local/bin/noblankprint-python..."
PYTHON_BIN=$(ls /opt/noblankprint-pvm/bin/python3* 2>/dev/null | grep -E 'python3\.[0-9]+$' | head -n 1)
if [ -z "${PYTHON_BIN}" ]; then
    PYTHON_BIN="/opt/noblankprint-pvm/bin/python3"
fi

if [ ! -f "${PYTHON_BIN}" ]; then
    echo "Error: Python binary not found in /opt/noblankprint-pvm/bin!"
    exit 1
fi

sudo mkdir -p /usr/local/bin
sudo ln -sf "${PYTHON_BIN}" /usr/local/bin/noblankprint-python

echo "[3/3] Verifying installation..."
/usr/local/bin/noblankprint-python --version
echo "NoBlankPrintPVM installed successfully at /usr/local/bin/noblankprint-python -> ${PYTHON_BIN}"
