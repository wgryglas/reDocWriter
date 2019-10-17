FROM ubuntu

RUN apt-get -q update
RUN apt-get install -q python
RUN apt-get install -q python-pip
RUN pip install --no-cache-dir --upgrade setuptools
RUN pip install --no-cache-dir --upgrade docutils
RUN pip install --no-cache-dir --upgrade gitpython
RUN pip install --no-cache-dir --upgrade PySide
RUN pip install --no-cache-dir --upgrade pyqode.core
RUN pip install --no-cache-dir --upgrade pyqode.rst
RUN pip install --no-cache-dir --upgrade pyqode.core
RUN pip install --no-cache-dir --upgrade PyInstaller


ENTRYPOINT ["pyinstaller"]