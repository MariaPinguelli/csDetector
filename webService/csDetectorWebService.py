import flask
import os, sys
p = os.path.abspath('.')
sys.path.insert(1, p)
from flask import jsonify, request, send_file
from csDetectorAdapter import CsDetectorAdapter
 
app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/"


@app.route('/getSmells', methods=['GET'])
def getSmells():
    needed_graphs = False
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

    if 'graphs' in request.args:
            needed_graphs = bool(request.args['graphs'])    
    try:
        os.mkdir("../out/output_"+user)
    except:
        pass

    tool = CsDetectorAdapter()
    formattedResult, result, config = tool.executeTool(repo, pat, outputFolder="out/output_"+user)

    if needed_graphs:
        path = os.path.join(config.resultsPath, f"commitCentrality_0.pdf")
        print(path)

    r = jsonify({"result": result, "files":[path]})
    return r

@app.route('/uploads/<path:filename>')
def download_file(filename):
    fn = os.path.join(os.getcwd(), filename)
    print(fn)
    return send_file(fn)
 

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello!</h1><p>To execute csDetector, please try running /getSmells?repo=REPOSITORY_URL&pat=GIT_PAT.</p>"


app.run(port=5001, threaded=True)
