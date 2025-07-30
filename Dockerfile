FROM texlive/texlive:latest-basic

WORKDIR /usr/src/app

COPY app.py .
COPY run .
RUN chmod +x run
COPY static ./static


# Installing system packages
RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip python3-venv poppler-utils -y

# Installing tex-live packages for tikzpicture
RUN tlmgr option repository http://mirror.ctan.org/systems/texlive/tlnet
RUN tlmgr update --self
RUN tlmgr install standalone pgf pgfplots etoolbox

# Create virtual env and installing python packages
ENV VIRTUAL_ENV=/usr/src/app/venv
ENV PATH="$VIRTUAL_ENV/bin":"$PATH"
RUN python3 -m venv $VIRTUAL_ENV
RUN pip install --upgrade pip
RUN pip install --no-cache-dir gradio==5.38.2

# Gradio server info
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

ENTRYPOINT ["./run"]