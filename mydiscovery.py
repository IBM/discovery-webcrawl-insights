from flask import Flask, redirect, request,render_template
import json
from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
import os.path
from os import path
from datetime import datetime
import logging


app = Flask(__name__, template_folder="", static_folder="", static_url_path='')
collection_id = ""
environment_id = ""
apikey = ""
service_url = ""
port = int(os.getenv('PORT', 8000))
vcap = {}

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    logging.warning('Found VCAP_SERVICES')
    if 'discovery' in vcap:
        creds = vcap['discovery'][0]['credentials']
        apikey = creds['apikey']
        service_url = creds['url']
elif os.path.isfile('credentials.json'):
    with open('credentials.json') as f:
        logging.warning('Reading from credentials.json file...')
        creds = json.load(f)
        apikey = creds['apikey']
        service_url = creds['url']

logging.warning("in discovery.py...")
logging.warning("Service URL is "+service_url)

authenticator = IAMAuthenticator(apikey)
discovery = DiscoveryV1(
   version='2018-08-01',
   authenticator=authenticator)
discovery.set_service_url(service_url)

@app.route("/askquery")
def askquery():
  global discovery;
  environments = discovery.list_environments().get_result();
  byod_environments = [x for x in environments['environments'] if x['name'] == 'byod']
  byod_environment_id = byod_environments[0]['environment_id']
  global environment_id;
  environment_id = byod_environment_id;
  collections = discovery.list_collections(byod_environment_id).get_result()
  msgs = {}
  now = datetime.now()

  if len(collections["collections"]) == 0:
    msgs['title'] = "No collection found!"
    msgs['subtitle'] = "Create a new collection."
    now = datetime.now()
  else:
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    msgs['time'] = dt_string
    msgs['title'] = "Collection - " + collections["collections"][0]["name"]
    msgs['subtitle'] = "Query this collection, get status or delete the collection"

  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  msgs['time'] = dt_string
  return render_template("query.html", results={}, search="Enter a new search...", msg=msgs)

@app.route('/')
def index():
  global discovery;
  environments = discovery.list_environments().get_result();
  logging.warning("Listing environments:")
  logging.warning(json.dumps(environments))
  byod_environments = [x for x in environments['environments'] if x['name'] == 'byod']
  byod_environment_id = byod_environments[0]['environment_id']
  global environment_id;
  environment_id = byod_environment_id;
  collections = discovery.list_collections(byod_environment_id).get_result()
  msgs = {}
  now = datetime.now()

  if len(collections["collections"]) == 0:
    msgs['title'] = "No collection found!"
    msgs['subtitle'] = "Create a new collection."
    now = datetime.now()
  else:
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    msgs['time'] = dt_string
    msgs['title'] = "Collection - " + collections["collections"][0]["name"]
    msgs['subtitle'] = "Query this collection, get status or delete the collection"

  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  msgs['time'] = dt_string
  return render_template("query.html", results={}, search="Enter a new search...", msg=msgs)

# If you have additional modules that contain your API endpoints, for instance
# using Blueprints, then ensure that you use relative imports, e.g.:
# from .mymodule import myblueprint

@app.route('/query', methods = ['GET', 'POST'])
def get_results():
  query = "";
  if request.method == 'POST':
    query = request.form.get('search');
  elif request.method == 'GET':
    query = request.args.get('search');
  global environment_id;

  environments = discovery.list_environments().get_result();
  byod_environments = [x for x in environments['environments'] if x['name'] == 'byod']
  byod_environment_id = byod_environments[0]['environment_id']

  environment_id = byod_environment_id;
  collections = discovery.list_collections(byod_environment_id).get_result()
  print(collections)
  byod_collections = [x for x in collections['collections']]
  global collection_id;

  msgs = {}
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  msgs['time'] = dt_string
  if len(collections["collections"]) == 0:
    msgs['title'] = "No collection found!"
    msgs['subtitle'] = "Create a new collection."
    now = datetime.now()
    return render_template('query.html', results={}, search="Enter a new search...", msg=msgs)
  else:
    msgs['title'] = "Collection - " + collections["collections"][0]["name"]
    msgs['subtitle'] = "Query this collection, get status or delete the collection..."
    collection_id = byod_collections[0]["collection_id"]
    query_results = discovery.query(
                    environment_id,
                    collection_id,
                    natural_language_query=query,
                    count=1000,
                    highlight="true",
                    passages="true"
                    ).get_result()
    document_url_map = {};
    allres = query_results["results"];
    for res in allres:
      document_url_map[res["id"]] = res["metadata"]["source"]["url"];

    query_results["documenturlmap"] = document_url_map;
    results=json.dumps(query_results, indent=2);
    return render_template('query.html', results=results, search=query, msg=msgs)

@app.route('/createcollection', methods = ['GET', 'POST'])
def create_collection():
  urls = "";
  name = "mycollection"
  if request.method == 'POST':
    urls = request.form.get('urls');
    name = request.form.get('name');
  elif request.method == 'GET':
    urls = request.args.get('urls');
    name = request.args.get('name');

  urlsplit = urls.split(",");
  urlarray = [];
  for url in urlsplit:
    urlstring = {}
    urlstring["url"] = url;
    urlarray.append(urlstring)

  print(urlarray)
  name = '"'+name +'"'

  environments = discovery.list_environments().get_result();
  byod_environments = [x for x in environments['environments'] if x['name'] == 'byod']
  byod_environment_id = byod_environments[0]['environment_id']
  global environment_id;
  environment_id = byod_environment_id;

  config_data = """{
      "name": """ + name +""",
      "description": "Crawl the code patterns",
      "conversions": {
        "html": {
          "aggressive_cleanup": true,
          "exclude_tag_attributes": [
            "style",
            "class"
          ],
          "exclude_tags_completely": [
            "style",
            "script",
            "header",
            "footer",
            "meta"
          ]
        },
        "json_normalizations": [
          {
            "operation": "remove_nulls"
          }
        ]
      },
      "enrichments": [
        {
          "destination_field": "enriched_text",
          "enrichment": "natural_language_understanding",
          "options": {
            "features": {
              "categories": {},
              "concepts": {
                "limit": 8
              },
              "entities": {
                "emotion": false,
                "limit": 50,
                "sentiment": false
              }
            }
          },
          "source_field": "text"
        }
      ],
      "source": {
        "options": {
          "urls": """ + json.dumps(urlarray) + """
        },
        "schedule": {
          "enabled": true,
          "frequency": "weekly",
          "time_zone": "America/New_York"
        },
        "type": "web_crawl"
      }
  }"""


  data = json.loads(config_data)
  new_config = discovery.create_configuration(
            byod_environment_id,
            data['name'],
            description=data['description'],
            conversions=data['conversions'],
            enrichments=data['enrichments'],
            source=data['source']).get_result()

  new_config_id = new_config["configuration_id"]
  new_collection = discovery.create_collection(
        environment_id=byod_environment_id,
        configuration_id=new_config_id,
        name=name,
        description='custom collection',
        language='en').get_result();
  print(json.dumps(new_collection, indent=2));
  global collection_id;
  collection_id = new_collection["collection_id"];
  msgs = {}
  msgs['title'] = "Created Collection - " + new_collection["name"]
  msgs['subtitle'] = "Query this collection, get the status or delete the collection..."
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  msgs['time'] = dt_string
  return render_template("query.html", results={}, search="Enter a new search...", msg=msgs)

@app.route('/getstatus', methods = ['GET'])
def get_collection_status():
  environments = discovery.list_environments().get_result();
  byod_environments = [x for x in environments['environments'] if x['name'] == 'byod']
  byod_environment_id = byod_environments[0]['environment_id']
  global environment_id;
  environment_id = byod_environment_id;
  collections = discovery.list_collections(byod_environment_id).get_result()
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  msgs = {}
  msgs['time'] = dt_string
  if len(collections["collections"]) == 0:
    msgs['title'] = "No collection found!"
    msgs['subtitle'] = "Create a new collection."
    return render_template('query.html', results={}, search="Enter a new search...", msg=msgs)
  else:
    coll = collections["collections"][0];
    status = discovery.get_collection(
                      environment_id,
                      coll["collection_id"]).get_result()["document_counts"];
    msgs['title'] = "Status of the collection  - " + coll["name"]
    msgs['subtitle'] = "The number documents available = "+str(status["available"]) + ", processing = "+str(status["processing"])+", and failed ="+str(status["failed"])+". Query this collection, get the status or delete the collection..."
    now = datetime.now()
    return render_template("query.html", results="query", search="Search", msg=msgs);


@app.route('/deletecollections', methods=['GET'])
def delete_collection():
  environments = discovery.list_environments().get_result();
  byod_environments = [x for x in environments['environments'] if x['name'] == 'byod']
  byod_environment_id = byod_environments[0]['environment_id']
  global environment_id;
  environment_id = byod_environment_id;
  collections = discovery.list_collections(byod_environment_id).get_result()

  msgs = {}
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  msgs['time'] = dt_string

  if len(collections["collections"]) == 0:
    msgs['title'] = "No collection found!"
    msgs['subtitle'] = "Create a new collection."
    return render_template('query.html', results={}, search="Enter a new search...", msg=msgs)
  else:
    coll = collections["collections"][0];
    delete_collection = discovery.delete_collection(
                            environment_id,
                            coll["collection_id"]).get_result()
    print(json.dumps(delete_collection, indent=2))
    configs = discovery.list_configurations('b679a4a8-0d5a-4e6b-9886-56fed40225c8').get_result()
    configarray = configs["configurations"]
    for config in configarray:
      if config["name"] == "Default Configuration":
          print("Skipping default configuration!")
      else:
          config_delete = discovery.delete_configuration(environment_id, config["configuration_id"]).get_result()
          print(json.dumps(config_delete, indent=2))
    msgs['title'] = "Deleted Collection - " + coll["name"]
    msgs['subtitle'] = "Create a collection, query, get status of an existing collection..."
    return render_template("query.html", results="query", search="Search", msg=msgs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
