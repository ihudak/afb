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
ENV DT_LOGLEVEL_PROC="general=info,hooking=info,pgid=info,hooking=info"
ENV DT_LOGCON_PROC=stdout
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
COPY ./src .
COPY ./requirements.txt .

############################################################
# install dependencies
############################################################
RUN pip install -r ./requirements.txt


#ENTRYPOINT ["python", "main.py"]
ENTRYPOINT export PATH=$PATH:$OA_INSTALL_DIR:$OA_INSTALL_DIR/agent && \
           if [ -n "${TENANT_URL+x}" ] && [ -n "${OA_TOKEN+x}" ]; then \
                /opt/get_oa.sh ; \
                /opt/config_oa.sh ; \
                LD_PRELOAD=$OA_INSTALL_DIR/agent/lib64/liboneagentproc.so python ./main.py ; \
           else \
                python ./main.py ; \
           fi

