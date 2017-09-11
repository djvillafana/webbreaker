# Image: webbreaker:latest
# Date: 9/6/2017
FROM centos:latest

RUN yum -y install unzip && \
# Start by making sure your system is up-to-date:
  yum update && \
# Compilers and related tools:
  yum groupinstall -y "development tools" && \
# Libraries needed during compilation to enable all features of Python:
  yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel && \
# If you are on a clean "minimal" install of CentOS you also need the wget tool:
  yum install -y wget

# Python 2.7.13:
RUN wget http://python.org/ftp/python/2.7.13/Python-2.7.13.tar.xz --no-check-certificate && \
  tar xf Python-2.7.13.tar.xz && \
  cd Python-2.7.13 && \
  ./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib" && \
  make && make altinstall

# Python 3.6.2:
RUN wget http://python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz --no-check-certificate && \
  tar xf Python-3.6.2.tar.xz && \
  cd Python-3.6.2 && \
  ./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib" && \
  make && make altinstall

# Strip the Python 2.7 binary:
RUN strip /usr/local/lib/libpython2.7.so.1.0 && \
# Strip the Python 3.6 binary:
  strip /usr/local/lib/libpython3.6m.so.1.0

RUN wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate && \
  python get-pip.py && \
  python2.7 get-pip.py && \
  python3.6 get-pip.py

ENV PKG_CONFIG_PATH /Python-3.6.2/build/temp.linux-x86_64-3.6/libffi:/Python-2.7.13/build/temp.linux-x86_64-2.7/libffi

RUN export PATH=$PATH:$PYTHONPATH && \
  pip2.7 install cryptography && \
  pip3.6 install cryptography && \
  yum -y install libffi-devel

COPY . /webbreaker

RUN cd /webbreaker && \
    python2.7 setup.py install --user && \
    python3.6 setup.py install --user

CMD ["/usr/sbin/init"]