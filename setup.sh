#!/bin/bash
python3 -m venv venv;
source venv/bin/activate && pip3 install -r organizations/requirements.txt;
cd organizations && echo -e "FLASK_ENV=testing\nSECRET_KEY=dont_forget_to_change_me_bro\nEGRUL_SERVICE_URL=http://localhost:28961/" > .env;
flask db upgrade && echo "setup has been completed";
python3 fill_demo_data.py;