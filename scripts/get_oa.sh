#!/bin/sh

# clear the OA directory
rm -rf $OA_INSTALL_DIR && mkdir -p $OA_INSTALL_DIR

# MINSIZE is 5 MB
export MINSIZE=500000

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
# Download OA (Java Agent only)
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

echo "Downloading the Python Agent..."
# download python agent
wget "$python_agent_url" -O $PYTHON_AGENT_ZIP
echo "Checking if PythonAgent.zip file is ok"
if [ ! -e "$PYTHON_AGENT_ZIP" ]; then
  echo "PythonAgent.zip does not exist.";
  exit 1;
fi

FILESIZE=$(stat -c%s "$PYTHON_AGENT_ZIP")
export FILESIZE
if [ $FILESIZE -lt $MINSIZE ]; then
  echo "$PYTHON_AGENT_ZIP is too small. Please check it for errors";
  exit 1;
else
  echo "$PYTHON_AGENT_ZIP download is ok";
  stat -c%s "$PYTHON_AGENT_ZIP";
fi

# Unzip OA
echo "Upzipping OneAgent"
cd "$OA_INSTALL_DIR" && unzip "$AGENT_ZIP" # && rm "$AGENT_ZIP"
echo "Upzipping PythonAgent"
cd "$OA_INSTALL_DIR"/agent/lib64 && unzip "$PYTHON_AGENT_ZIP" # && rm "$PYTHON_AGENT_ZIP"

# copy the template of the config file
cp /opt/standalone.conf "$OA_INSTALL_DIR"/agent/conf/

cd /opt && unzip /opt/oneagentpython.zip
mkdir -p /opt/bot/src
mkdir -p /opt/bot/any
mkdir -p /opt/bot/agent/any
mkdir -p "$OA_INSTALL_DIR"/agent/any/
ln -s /opt/oneagentpython /opt/bot/agent/any/python
ln -s /opt/oneagentpython /opt/bot/any/python
ln -s /opt/oneagentpython "$OA_INSTALL_DIR"/agent/any/python
ls -la "$OA_INSTALL_DIR"/agent/any/python

sleep 5

echo "OA load done"
