FROM ubuntu

RUN pip install --no-cache-dir --upgrade setuptools
RUN pip install --no-cache-dir --upgrade docutils
RUN pip install --no-cache-dir --upgrade gitpython
RUN pip install --no-cache-dir --upgrade PySide
RUN pip install --no-cache-dir --upgrade pyqode.core
RUN pip install --no-cache-dir --upgrade pyqode.rst
RUN pip install --no-cache-dir --upgrade pyqode.core
RUN pip install --no-cache-dir --upgrade PyInstaller


ENTRYPOINT ["pyinstaller"]