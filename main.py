from app.models.document import Document
from system.loader.loader import Loader
from app.models.searcher import Searcher
from config.config import config

from flask import Flask
from flask import request, jsonify

class App:
    
    def __init__(self):
        loader = Loader()
        document = Document(loader, "post", ["title", "content"])
        
        fields = {
            "index" : ["title"],
            "show"  : ["title", "update_time"],
            "primary": "_id"
        }
        self.searcher = Searcher(document, fields)
        self.searcher.fit()
        # while True:
        #     query = input("Enter your query: ")
        #     searcher.search(query)
        #     print("\n" * 4)
    def search(self, query):
        return self.searcher.search(query)
        


# Main()
_app = App()
app = Flask(__name__)
@app.route("/", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        query = request.form.get('query')
        data = _app.search(query)
        return jsonify(isError=False, message="Success", statusCode=200, data=data), 200

if __name__ == '__main__':
    host, port = config["server"]["host"], config["server"]["port"]
    app.run(host=host, port=port)