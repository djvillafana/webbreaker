# Image: webbreaker:latest
# Date: 9/15/2017
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

# Python 3.6.2:
RUN wget http://python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz --no-check-certificate && \
  tar xf Python-3.6.2.tar.xz && \
  cd Python-3.6.2 && \
  ./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib" && \
  make && make altinstall

# Strip the Python 3.6 binary:
RUN strip /usr/local/lib/libpython3.6m.so.1.0

RUN wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate && \
  python get-pip.py && \
  python3.6 get-pip.py

ENV PKG_CONFIG_PATH /Python-3.6.2/build/temp.linux-x86_64-3.6/libffi:/Python-2.7.13/build/temp.linux-x86_64-2.7/libffi
ENV LC_ALL en_US.utf8
ENV LANG en_US.utf8
RUN export PATH=$PATH:$PYTHONPATH && \
  yum -y install libffi-devel

# Copies files from repository into webbreaker directory
COPY . /webbreaker

# When building your docker image you will need your specific webinspect.ini and email.ini to be included in your 
# build and overwrite the default files. After cloning the repository copy those two files to the root directory 
# and then uncomment the following lines:

# COPY webinspect.ini /home/webinspect.ini
# COPY email.ini /home/email.ini
# RUN cd /home && \
#  cp -f webinspect.ini /webbreaker/webbreaker/etc && \
#  cp -f email.ini /webbreaker/webbreaker/etc

RUN cd /webbreaker && \
  pip3.6 install -r requirements.txt && \
  python3.6 setup.py install

CMD ["/usr/sbin/init"]
