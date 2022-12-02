python3 -m venv venv;
source venv/bin/activate && pip3 install -r requirements.txt;
echo -e "FLASK_APP=organizations\nFLASK_ENV=development\nSECRET_KEY=dont_forget_to_change_me_bro" > .env;
flask db upgrade && echo "setup has been completed"