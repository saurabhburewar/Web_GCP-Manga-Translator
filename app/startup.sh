set -ev

apt-get update
apt-get install -yq git supervisor python python-pip python3-distutils
pip install --upgrade pip virtualenv

export HOME=/root
git clone https://github.com/saurabhburewar/Web_GCP-Manga-Translator /app

sudo bash /app/add-google-cloud-ops-agent-repo.sh --also-install

useradd -m -d /home/pythonapp pythonapp

virtualenv -p python3 /app/env
/bin/bash -c "source /app/env/bin/activate"
/app/env/bin/pip install -r /app/requirements.txt

chown -R pythonapp:pythonapp

cp /app/python-app.conf /etc/supervisor/conf.d/python-app.conf

supervisorctl reread
supervisorctl update
