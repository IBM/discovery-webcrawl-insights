from flask import Flask, redirect, request,render_template
import json
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
import os.path
from os import path
from datetime import datetime
import logging
import requests
from requests.structures import CaseInsensitiveDict
import base64


app = Flask(__name__, template_folder="", static_folder="", static_url_path='')
collection_id = ""
project_id = "null"
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
discovery = DiscoveryV2(
   version='2020-08-30',
   authenticator=authenticator)
discovery.set_service_url(service_url)

@app.route("/createproject")
def createproject():
  discovery.create_project('Example Project', 'document_retrieval');
  logging.warning("Created project successfully!");

@app.route("/askquery")
def askquery():
  global discovery;
  global project_id;

  response = discovery.list_projects();
  projlist = response.result;
  logging.warning("Project ID is " + project_id);

  for prj in projlist["projects"]:
    if prj['name'] == 'Example Project':
      project_id = prj['project_id'];

  logging.warning("Project ID is "+ project_id);
  if project_id == "null":
    logging.info("Creating the project Example...")
    createproject();
    for prj in projlist["projects"]:
      print(prj)
      if prj['name'] == 'Example Project':
        project_id = prj['project_id'];
  logging.warning("Project ID is " + project_id);
  collections = discovery.list_collections(project_id).result;
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
  logging.warning("Rendering the web page..")
  return render_template("query.html", results={}, search="Enter a new search...", msg=msgs)

@app.route('/')
def index():
  return askquery();

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

  global project_id;

  response = discovery.list_projects();
  projlist = response.result;
  for prj in projlist["projects"]:
      if prj['name'] == 'Example Project':
          project_id = prj['project_id'];

  collections = discovery.list_collections(project_id).result;
  print(collections)

  global collection_id;
  collection_id = collections["collections"][0]["collection_id"];

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
    collection_id = ["collection_id"]
    query_results = discovery.query(project_id="152aab65-6006-4329-8ff4-ed3a7018cd68",
                    collection_ids=["9e302195-7391-3044-0000-017c6012a84d"],
                    highlight="true",
                    natural_language_query="kubernetes").get_result();
    # query_results = discovery.query(
   #                project_id,
    #             [collection_id],
   #            natural_language_query=query
    #                ).get_result()
    document_url_map = {};
    allres = query_results["results"];
    for res in allres:
      document_url_map[res["document_id"]] = res["metadata"]["source"]["url"];

    query_results["documenturlmap"] = document_url_map;
    results=json.dumps(query_results, indent=2);
    return render_template('query.html', results=results, search=query, msg=msgs)

@app.route('/createcollection', methods = ['GET', 'POST'])
def create_collection():
  urls = "";
  global project_id;
  response = discovery.list_projects();
  projlist = response.result;
  for prj in projlist["projects"]:
    if prj['name'] == 'Example Project':
      project_id = prj['project_id'];

  name = "examplecollection"
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
    urlstring["maximum_hops"]= 2
    urlstring["blacklist"]= []
    urlstring["override_robots_txt"]= "true";
    urlarray.append(urlstring)

  print(urlarray)
  name = '"'+name +'"'
  keywords_enrichment_id = "";
  entities_enrichment_id = "";
  res = discovery.list_enrichments(project_id)
  enrichments = res.result["enrichments"]
  keywords_enrichment_id = ""
  entities_enrichment_id = ""
  for encr in enrichments:
      if encr["name"] == "Keywords":
          keywords_enrichment_id = encr["enrichment_id"];
      elif encr["name"] == "Entities v2":
          entities_enrichment_id = encr["enrichment_id"];


  new_collection = discovery.create_collection(
        project_id=project_id,
        name=name,
        description='custom collection',
        language='en').get_result();
  print(json.dumps(new_collection, indent=2));

  apikey_string = "apikey:"+apikey
  apikey_string_bytes = apikey_string.encode("ascii")

  base64_bytes = base64.b64encode(apikey_string_bytes)
  base64_string = base64_bytes.decode("ascii")

  print(f"Encoded string: {base64_string}")
  headers = CaseInsensitiveDict()
  headers["x-watson-discovery-next"] = "true"
  headers["Content-Type"] = "application/x-www-form-urlencoded"
  headers["Authorization"] = "Basic "+base64_string

  data = """
  {
    "source": {
      "type" : "web_crawl",
      "credential_id" : "",
      "schedule" : {
        "enabled" : true,
        "time_zone" : null,
        "frequency" : "monthly"
      },
      "options" : {
         "urls[": """ + json.dumps(urlarray) + """]
      }
    }
  }
  """

  global service_url
  resp = requests.post(service_url, headers=headers, data=data)

  print(resp.status_code)

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
  global project_id;
  response = discovery.list_projects();
  projlist = response.result;
  for prj in projlist["projects"]:
    if prj['name'] == 'Example Project':
      project_id = prj['project_id'];
  collections = discovery.list_collections(project_id).get_result()
  logging.warning(collections);
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
    print(discovery.get_collection(
                      project_id,
                      coll["collection_id"]).get_result());
    status = discovery.get_collection(
                      project_id,
                      coll["collection_id"]).get_result()["document_counts"];
    msgs['title'] = "Status of the collection  - " + coll["name"]
    msgs['subtitle'] = "The number documents available = "+str(status["available"]) + ", processing = "+str(status["processing"])+", and failed ="+str(status["failed"])+". Query this collection, get the status or delete the collection..."
    now = datetime.now()
    return render_template("query.html", results="query", search="Search", msg=msgs);


@app.route('/deletecollections', methods=['GET'])
def delete_collection():
  global project_id;
  collections = discovery.list_collections(project_id).get_result()

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
                            project_id,
                            coll["collection_id"]).get_result()
    print(json.dumps(delete_collection, indent=2))
    msgs['title'] = "Deleted Collection - " + coll["name"]
    msgs['subtitle'] = "Create a collection, query, get status of an existing collection..."
    return render_template("query.html", results="query", search="Search", msg=msgs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
