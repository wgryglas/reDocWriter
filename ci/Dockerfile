FROM ubuntu:18.04

RUN apt-get -q update
RUN apt-get install -q -y python
RUN apt-get install -q -y python-pip
#RUN apt-get install -q -y cmake
RUN pip install --no-cache-dir --upgrade setuptools
RUN pip install --no-cache-dir --upgrade docutils
RUN pip install --no-cache-dir --upgrade gitpython
#RUN pip install --no-cache-dir --upgrade PySide
RUN apt-get install -q -y python-pyside
RUN pip install --no-cache-dir --upgrade pyqode.core
RUN pip install --no-cache-dir --upgrade pyqode.rst
RUN pip install --no-cache-dir --upgrade pyqode.core
RUN pip install --no-cache-dir --upgrade PyInstaller


ENTRYPOINT ["pyinstaller"]