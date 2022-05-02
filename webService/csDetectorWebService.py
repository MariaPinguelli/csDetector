import flask
from flask import request


app = flask.Flask(__name__)


@app.route('/getSmells', methods=['GET'])
def getSmells():
    if 'repo' in request.args:
        repo = str(request.args['repo'])
        pat = str(request.args['pat'])
    else:
        return "Error: No id field provided. Please specify an id."
    # tool = CsDetectorAdapter()
    # print(tool.executeTool(repo, pat))
    return "<p>ueeee</p>"


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello!</h1><p>To execute csDetector, please try running /getSmells?repo=REPOSITORY_URL&pat=GIT_PAT.</p>"


app.run()
