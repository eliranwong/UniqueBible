cd ~
wget "https://github.com/eliranwong/UniqueBible/archive/master.zip"
unzip master.zip
cd UniqueBible-master
python3 -m venv venv
source venv/bin/activate
pip3 install PySide2
pip3 install PyPDF2
pip3 install python-docx
pip3 install gdown