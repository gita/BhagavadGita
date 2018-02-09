from flask import Blueprint
from flask import render_template


docs = Blueprint('Docs', __name__, url_prefix="/docs")


@docs.route('/', methods=['GET', 'POST'])
def get_docs():

    return render_template('docs/index.html')
