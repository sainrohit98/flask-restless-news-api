# News Flask-Restless API

## Requirements

* Python 3.x (pip + virtualenv will probably still work)

## Installation

1. download this repository and generate a fresh virtual
   environment:

    ```
    # change into the repository's base directory
    cd flask-restless-news-api

    # create a virtual environment, into which you'll install all the
    # dependencies for this project; Python 2.x, use 'virtualenv' instead
    python3 -m venv venv

    # activate the virtual environment
    source venv/bin/activate
    ```

2. Install necessary Python packages using `pip`:

    ```
    pip install -r requirements.txt
    ```

3. Tell Flask where to find the app, initialize the `newsdata` database, and
   launch the Flask web application:

    ```
    # for Windows Command Prompt, do 'set FLASK_APP=newsapp\app.py'
    export FLASK_APP=newsapp/app.py
    export FLASK_DEBUG=1  # for template auto-reloading
    flask initdb
    flask run             # defaults to http://127.0.0.1:5000
    ```
   
## Rest APIs

    ```
    [GET] /api/v1/news/search (saved news in model)
    [GET] /api/v1/news/searchDirect (direct news fetch from third party api)

    Note:- you can use browser for hitting apis eg. http://127.0.0.1:5000/api/v1/news/search
    ```
