yum install -y git
git clone https://github.com/baolintian/feature_judge_template.git
yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel lrzsz
wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz
tar -zxvf Python-3.9.1.tgz
cd Python-3.9.1
./configure prefix=/usr/local/python3
make && make install
ln -s /usr/local/python3/bin/python3.9 /usr/bin/python3 
ln -s /usr/local/python3/bin/pip3.9 /usr/bin/pip3
/usr/local/python3/bin/python3.9 -m pip install --upgrade pip
cd ..
cd feature_judge_template/
pip3 install -r requirements.txt
cd code
python3 ./00_064MP.py

