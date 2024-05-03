#!/bin/sh

# clear the OA directory
rm -rf $OA_INSTALL_DIR && mkdir -p $OA_INSTALL_DIR

# MINSIZE is 5 MB
export MINSIZE=5000000
export PYTHON_MINSIZE=500000
export PYTHON_SOFT_SIZE=25000

# define platform param for the Dynatrace API call
PLATFORM=$(uname -p);
export PLATFORM;
if [ "$PLATFORM" = "arm" ] || [ "$PLATFORM" = "arm64" ] || [ "$PLATFORM" = "aarch64" ]; then
  export PLATFORM="arm";
elif [ $PLATFORM = "x86" ] || [ $PLATFORM = "x86_64" ] || [ $PLATFORM = "x64" ]; then
  export PLATFORM="x86";
else
  export PLATFORM="x86";
fi

echo "Downloading the latest OneAgent..."
# Download OA (Standalone Agent only)
curl --request GET -sL \
--url "$TENANT_URL/api/v1/deployment/installer/agent/unix/paas/latest?flavor=default&arch=$PLATFORM&bitness=64&include=java&skipMetadata=true" \
--header 'accept: application/octet-stream' \
--header "Authorization: Api-Token $OA_TOKEN" \
--output "$AGENT_ZIP"

echo "Checking if OneAgent.zip file is ok"
if [ ! -e "$AGENT_ZIP" ]; then
  echo "OneAgent.zip does not exist.";
  exit 1;
fi

FILESIZE=$(stat -c%s "$AGENT_ZIP")
export FILESIZE
if [ $FILESIZE -lt $MINSIZE ]; then
  echo "$AGENT_ZIP is too small. Please check it for errors";
  exit 1;
else
  echo "$AGENT_ZIP download is ok";
  stat -c%s "$AGENT_ZIP";
fi

echo "Downloading Python Native Agent..."
# download python agent
wget "$python_native_agent_url" -O $PYTHON_NATIVE_AGENT_ZIP
echo "Checking if $PYTHON_NATIVE_AGENT_ZIP file is ok"
if [ ! -e "$PYTHON_NATIVE_AGENT_ZIP" ]; then
  echo "$PYTHON_NATIVE_AGENT_ZIP does not exist.";
  exit 1;
fi

FILESIZE=$(stat -c%s "$PYTHON_NATIVE_AGENT_ZIP")
export FILESIZE
if [ $FILESIZE -lt $PYTHON_MINSIZE ]; then
  echo "$PYTHON_NATIVE_AGENT_ZIP is too small. Please check it for errors";
  exit 1;
else
  echo "$PYTHON_NATIVE_AGENT_ZIP download is ok";
  stat -c%s "$PYTHON_NATIVE_AGENT_ZIP";
fi

echo "Download Python Soft Agent..."
wget "$python_soft_agent_url" -O $PYTHON_SOFT_AGENT_ZIP
echo "Checking if $PYTHON_SOFT_AGENT_ZIP file is ok"
if [ ! -e "$PYTHON_SOFT_AGENT_ZIP" ]; then
  echo "$PYTHON_SOFT_AGENT_ZIP does not exist.";
  exit 1;
fi

FILESIZE=$(stat -c%s "$PYTHON_SOFT_AGENT_ZIP")
export FILESIZE
if [ $FILESIZE -lt $PYTHON_SOFT_SIZE ]; then
  echo "$PYTHON_SOFT_AGENT_ZIP is too small. Please check it for errors";
  exit 1;
else
  echo "$PYTHON_SOFT_AGENT_ZIP download is ok";
  stat -c%s "$PYTHON_SOFT_AGENT_ZIP";
fi

# Unzip OA
echo "Upzipping OneAgent"
cd "$OA_INSTALL_DIR" && unzip "$AGENT_ZIP" && rm "$AGENT_ZIP"
echo "Detecting the installation path for the Python agent"
export AGENT_VERSION=$(sed -n 2p "$OA_INSTALL_DIR"/manifest.json | grep version | sed -E s/\"version\":\ \"// | sed s/\",// |  tr -d ' ')
export PYTHON_AGENT_PATH="$OA_INSTALL_DIR/agent/bin/$AGENT_VERSION/any/python/"
echo "Agent Version detected: $AGENT_VERSION"
echo "Python Agent Path: $PYTHON_AGENT_PATH"

echo "Upzipping PythonNativeAgent"
cd "$OA_INSTALL_DIR"/agent/lib64 && unzip "$PYTHON_NATIVE_AGENT_ZIP" && rm "$PYTHON_NATIVE_AGENT_ZIP"
echo "Upzipping PythonSoftAgent"
mkdir -p "$PYTHON_AGENT_PATH" && \
  cd "$PYTHON_AGENT_PATH" && unzip "$PYTHON_SOFT_AGENT_ZIP" && rm "$PYTHON_SOFT_AGENT_ZIP"

# copy the template of the config file
cp /opt/standalone.conf "$OA_INSTALL_DIR"/agent/conf/

echo "OA load done"
