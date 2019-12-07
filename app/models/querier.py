from system.data_structures.sentence import Sentence
from config.config import config
import requests, json

class Query:

    def __init__(self, query):
        self.host, self.port = config["correct"]["host"], config["correct"]["port"]
        self.query = query
        self.process()
    
    def process(self):
        result = requests.post("http://%s:%s/" % (self.host, self.port), data={"query":"%s" % self.query})
        self.queries = json.loads(result.text)["data"]

    def transform(self, vectorizer):
        self.vectors = vectorizer.transform(self.queries)
        return self.vectors