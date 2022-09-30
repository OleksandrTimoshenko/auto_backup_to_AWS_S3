--------------------------------------------------------------------------------------------------

# Python script to backup files to AWS S3 bucket

### Install all needed packages::

* pip install -r requirements.txt

### Create AWS bucket && User with correct permissions and programmatic access

* Use this [link](https://danielpdev.io/create-user-access-programmatic-s3) for additional info

### Set correct credentials into .env.sample and rename in as .env

* cp .env.sample .env

### Run python script 
* python3 main.py

### Add cron task for script (additional step)
* crontab -e
* 0 12 * * * python3 /path/to/script/main.py
* crontab -l

--------------------------------------------------------------------------------------------------