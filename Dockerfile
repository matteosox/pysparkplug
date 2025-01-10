# Start from a core stack version
FROM quay.io/jupyter/scipy-notebook:2025-01-06

# Move to directory where repo will be mounted in home directory
WORKDIR /home/jovyan/pysparkplug

# Install requirements
COPY --chown=${NB_UID}:${NB_GID} . .
RUN SETUPTOOLS_SCM_PRETEND_VERSION=1.0 pip install --quiet --no-cache-dir --editable . && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
