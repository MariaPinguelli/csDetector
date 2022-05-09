import flask
import os, sys
p = os.path.abspath('.')
sys.path.insert(1, p)
from flask import jsonify, request
from csDetectorAdapter import CsDetectorAdapter
 


app = flask.Flask(__name__)


@app.route('/getSmells', methods=['GET'])
def getSmells():
    if 'repo' in request.args:
        repo = str(request.args['repo'])
        pat = str(request.args['pat'])
    else:
        return "Error: No id field provided. Please specify an id."
    tool = CsDetectorAdapter()
    result = tool.executeTool(repo, pat)
    r = jsonify(result) 
    return r
    

 

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello!</h1><p>To execute csDetector, please try running /getSmells?repo=REPOSITORY_URL&pat=GIT_PAT.</p>"


app.run(threaded=True)
