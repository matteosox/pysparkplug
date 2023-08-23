# Start from a core stack version
FROM jupyter/scipy-notebook:2023-05-15

# Move to directory where repo will be mounted in home directory
WORKDIR /home/jovyan/pysparkplug

# Install requirements
COPY --chown=${NB_UID}:${NB_GID} . .
RUN SETUPTOOLS_SCM_PRETEND_VERSION=1.0 pip install --quiet --no-cache-dir --editable . && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
