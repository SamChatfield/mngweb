MicrobesNG Website & Customer Portal
======================================

## Setup local dev environment

* Clone this repo
* Create a virtualenv in the top level directory `virtualenv -p python3 venv`
* Activate your venv `source venv/bin/activate`
* Install dependencies `pip install -r requirements/development.txt`
* Grab a recent copy of the database from the server backups in ``~/backups/microbesng.uk/db``
  and move it to your local repo `database/db.sqlite3`
* Grab local.py, either from the server or wherever it is kept in-house and move
  it to `source/mngweb/settings`
* You should now be able to start Django local server:
** `cd source`
** `python manage.py runserver`
* Access the local site at `http://localhost:8000`


## Deployment

1. Make sure you have fabric installed on your local machine `pip install fabric`
2. Make some changes
3. `git add` changes to your staging area and then `git commit`
3. `git push`
4. `cd ~/path/to/local/clone/deploy_tools`
5. `fab deploy:host=ubuntu@microbesng.uk`

To further understand what is going on, examine `fabfile.py` in the deploy_tools dir
