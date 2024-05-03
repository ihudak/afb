FROM ubuntu:jammy
LABEL authors="Natalia.Kadirova"

ENV TZ=Europe/Vienna \
    DEBIAN_FRONTEND=noninteractive

############################################################
# install python, zip, curl and wget
############################################################
RUN apt-get update && \
    apt-get install -y curl wget unzip python3-full python3-pip python-is-python3 && \
    rm -rf /var/lib/apt/lists/*

############################################################
# Prepare OA config
############################################################
ENV OA_INSTALL_DIR=/var/lib/dynatrace/oneagent
ENV AGENT_ZIP=$OA_INSTALL_DIR/OneAgent.zip
ENV PYTHON_NATIVE_AGENT_ZIP=/opt/PythonAgent.zip
ENV PYTHON_SOFT_AGENT_ZIP=/opt/PythonSoftAgent.zip
ENV OA_CONF_FILE=$OA_INSTALL_DIR/agent/conf/standalone.conf
ENV RUXIT_CONF_FILE=$OA_INSTALL_DIR/agent/conf/ruxitagentproc.conf
# Python Agent settings
ENV DT_PYTHON_NATIVE_LIBS_ROOT=$OA_INSTALL_DIR/agent/
#ENV DT_LOGLEVEL_PROC="general=none,hooking=none,pgid=none,hooking=none"
#ENV DT_LOGCON_PROC=stdout
ENV DT_DEBUGFLAGS="debugAllowCompanionConsoleLog=true,debugCompanionLeaveStdoutOpen=true,debugLogCompanionWorkerNative=true,debugLogCompanionWorkerLifecycleNative=true,debugLogAgentShutdownNative=true"
# Copy agent installer
COPY ./scripts/* /opt/
RUN chmod +x /opt/*.sh

############################################################
# set the current working directory for all commands
############################################################
WORKDIR /opt/bot

############################################################
# copy the project files
############################################################
COPY ./src/* .
COPY ./requirements.txt .

############################################################
# install dependencies
############################################################
RUN pip install -r ./requirements.txt

ENV python_native_agent_url="https://artifactory.lab.dynatrace.org/artifactory/agent-pipeline-test-local/com/compuware/apm/oneagentpython/oneagentpython-linux-x86_64-release/1.293.0.20240503-060637/oneagentpython-linux-x86_64-release-1.293.0.20240503-060637.zip"
ENV python_soft_agent_url="https://artifactory.lab.dynatrace.org/artifactory/ruxit-cluster-production-local/com/dynatrace/oneagent/python/oneagentpython/1.289.98.20240418-072830/oneagentpython-1.289.98.20240418-072830.zip"
ENV python_soft_agent_path="$OA_INSTALL_DIR/agent/bin/1.292.0.20240502-224326/any/python/"
ENV TENANT_ID=
ENV TENANT_LAYER=dev
ENV dt_srv=dynatracelabs.com
ENV TENANT_URL=
ENV OA_TOKEN=
############################################################
# Prepare OA. Download Agent
############################################################
RUN if [ -n "${TENANT_URL+x}" ] && [ -n "${OA_TOKEN+x}" ]; then \
      /opt/get_oa.sh ; \
      /opt/config_oa.sh ; \
    fi

#ENTRYPOINT ["python", "main.py"]
ENTRYPOINT export PATH=$PATH:$OA_INSTALL_DIR:$OA_INSTALL_DIR/agent && \
    printf %s $GSPREAD_AUTH > ./spreadsheet_auth.json && \
    sed -iE 's/\",\"/\",\n\ \ \"/g' ./spreadsheet_auth.json && \
    sed -iE 's/{\"/{\n\ \ \"/g' ./spreadsheet_auth.json && \
    sed -iE 's/\"}/\"\n}\n/g' ./spreadsheet_auth.json && \
    sed -iE 's/\":\"/\":\ \"/g' ./spreadsheet_auth.json && \
    sed -iE 's/-----BEGINPRIVATEKEY-----/-----BEGIN\ PRIVATE\ KEY-----/g' ./spreadsheet_auth.json && \
    sed -iE 's/-----ENDPRIVATEKEY-----/-----END\ PRIVATE\ KEY-----/g' ./spreadsheet_auth.json && \
    rm ./spreadsheet_auth.jsonE && \
    LD_PRELOAD=$OA_INSTALL_DIR/agent/lib64/liboneagentproc.so python ./main.py
