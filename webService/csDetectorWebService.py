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
    else:
        return "Error: No repo field provided. Please specify a repo.", 400

    if 'pat' in request.args:
        pat = str(request.args['pat'])
    else:
        return "Error: No pat field provided. Please specify a pat.", 400

    if 'user' in request.args:
        user = str(request.args['user'])
    else:
        user = "default" 

    try:
        os.mkdir("../out/output_"+user)
    except:
        pass

    tool = CsDetectorAdapter()
    formattedResult, result = tool.executeTool(repo, pat, outputFolder="out/output_"+user)
    r = jsonify(result)
    return r


 

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello!</h1><p>To execute csDetector, please try running /getSmells?repo=REPOSITORY_URL&pat=GIT_PAT.</p>"


app.run(port=5001, threaded=True)
