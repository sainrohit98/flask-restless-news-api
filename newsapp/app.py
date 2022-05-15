#!/usr/bin/env python
import json
import os
from dotenv import load_dotenv


from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from googletrans import Translator
from newsapi import NewsApiClient
import flask_restless
import click



basedir = os.path.dirname(__file__)
parentdir = os.path.join(os.path.dirname(__file__), '..')
load_dotenv()

# the default json file to load when you do 'flask initdb'
jsonfile = os.path.join(parentdir, 'news_table.json')

app = Flask(__name__)
app.config.from_pyfile('config.py')
api_key = app.config['API_KEY']


Bootstrap(app)

db = SQLAlchemy(app)


class NewsData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    desc_en = db.Column(db.String(1000))
    source = db.Column(db.String(100))
    news_id = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    name = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))
    title_en = db.Column(db.String(500))
    url = db.Column(db.String(200))

    def as_dict(self):
        """
        Return the entire table serialized as JSON

        (Note that you can also access the internal dictionary of SQLAlchemy
        objects with '.__dict__'.)
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Create the Flask-Restless API manager and make 'NewsData' available
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(NewsData, methods=['GET'], url_prefix=app.config['API_PREFIX'])

def converter(text):
    translator = Translator()
    source_lan = "en"
    translated_to = "fr"  # hi is the code for French Language

    # translate text  english to french
    translated_text = translator.translate(text, src=source_lan, dest=translated_to).text

    return translated_text

# ----------------------------------------------------------------------------
#                    R E S T     A P I     e n d p o i n t s
# ----------------------------------------------------------------------------

@app.route(app.config['API_PREFIX'] + '/news/search')
def search_newsdata():
    """Substring match on NewsData using the 'q=' query string parameter."""
    """ Add title_fr and desc_fr key in news_data """
    news_data = [match.as_dict() for match in NewsData.query.limit(10).all()]
    for articles in news_data:
        articles['title_fr'] = converter(articles['title_en'])
        articles['desc_fr']  = converter(articles['desc_en'])

    return jsonify({'news':news_data})


@app.route(app.config['API_PREFIX'] + '/news/searchDirect')
def get_news():
    newsapi = NewsApiClient(api_key=api_key)
    top_headlines = newsapi.get_top_headlines(sources="bbc-news")
    articles = top_headlines['articles']


    output = []
    separater1 = ''''''
    separater2 = ''''''
    alltitle = ''''''
    alldescription = ''''''
    for i in range(len(articles)):
        alltitle += separater1 + articles[i]['title']
        alldescription += separater2 + articles[i]['description']
        separater1 = '''**'''
        separater2 = '''!!'''
    text = alltitle + '''1!''' + alldescription
    french_text = converter(text)
    split_data = french_text.split('1!')
    french_titles = split_data[0].split('**')
    french_descriptions = split_data[1].split('!!')
    for i in range(len(articles)):
        my_articles = articles[i]
        id = my_articles['source']['id']
        name = my_articles['source']['name']
        title = my_articles['title']
        desc = my_articles['description']
        image_url = my_articles['urlToImage']
        source = my_articles['source']['id']
        author = my_articles['author']
        p_date = my_articles['publishedAt']
        content = my_articles['content'].replace('\r\n', '')
        url = my_articles['url']
        title_fr = french_titles[i]
        desc_fr = french_descriptions[i]

        output.append({'id': id, 'name': name, 'content': content, 'title_en': title, 'title_fr': title_fr,
                    'desc_fr':desc_fr,'desc_en': desc, 'image_url': image_url, 'source': source,'author': author,
                       'timestamp': p_date, 'url': url})

    data = {"news": output}

    return data



# ----------------------------------------------------------------------------
#                c o m m a n d - l i n e    o p e r a t i o n s
# ----------------------------------------------------------------------------


@app.cli.command()
@click.option('jsonfile', '--from-file', type=click.File(), default=jsonfile,
              help='Load data from json file.')
def initdb(jsonfile):
    """Create 'newsdata' table if it doesn't exist."""
    click.secho("Creating database tables for '{}'... "
                .format(app.config['SQLALCHEMY_DATABASE_URI']), fg='yellow',
                nl=False)

    # This create the table and the schema
    db.drop_all()
    db.create_all()

    # for data in jsonfile.read():
    news_data = json.loads(jsonfile.read().replace('\\"', "'"))

    for news in news_data['news']:
        db.engine.execute('''INSERT INTO news_data (author,content,desc_en,news_id,image_url,name,source,timestamp,title_en,url) VALUES("%s", "%s" ,"%s", "%s" ,"%s","%s", "%s" ,"%s", "%s" ,"%s")''' % (news['author'], news['content'], news['desc_en'], news['id'], news['image_url'],
                                                                                                                                                                                               news['name'],news['source'], news['timestamp'], news['title_en'], news['url']))


    click.secho('done\n', fg='green')


@app.cli.command()
@click.option('--with-ids', is_flag=True, default=False,
              help='Include unique IDs with each record.')
@click.option('--as-json', is_flag=True, default=False,
              help='Dump in comma-separated value format.')
def dumpdb(with_ids, as_json):
    """Dump contents of database to the terminal."""
    sep = '\t'

    if as_json:
        with_ids = True
        sep = ','
        cols = [[col.name, col.author]  for col in NewsData.__table__.columns]

        click.echo(','.join(cols))
    for rec in NewsData.query.all():
        cols = [rec.name, rec.author, rec.news_id, rec.source, rec.title_en, rec.desc_en, rec.image_url, rec.url, rec.content, rec.timestamp ]


        if with_ids:
            cols.insert(0, str(rec.id))

        click.echo(sep.join(cols))


if __name__ == '__main__':
    # You could specify host= and port= params here, but they won't be used if
    # you invoke the app in the usualy way with 'flask run'
    #app.run()

    click.secho('\nPlease launch the demo API with\n', err=True)
    click.secho('    export FLASK_APP=newsapp/app.py', bold=True,
                err=True)
    click.secho('    flask run [--host=X.X.X.X] [--port=YYYY]\n', bold=True,
                err=True)
