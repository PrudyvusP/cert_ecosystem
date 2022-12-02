python3 -m venv venv;
source venv/bin/activate && pip3 install -r requirements.txt;
echo -e "FLASK_APP=organizations\nFLASK_ENV=testing\nSECRET_KEY=dont_forget_to_change_me_bro" > .env;
mv .env organizations/;
flask db upgrade && echo "setup has been completed";
python3 fill_demo_data.py;