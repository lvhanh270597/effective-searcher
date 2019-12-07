from app.models.vectorizer import Vectorizer
from app.models.querier import Query
import numpy as np
import operator
import time
import faiss

class Searcher:

    def __init__(self, document, fields, number_results=10):
        self.number_results = number_results
        self.document = document
        self.set_fields(fields)
        self.document.fit()
    
    def set_fields(self, fields):
        self.fields = fields
        self.primary_field = fields["primary"]

    def set_docs(self, docs):
        self.docs = docs
        self.indexed_docs = dict()
        for field in self.fields["index"]:
            data_field = []
            for doc in docs:
                data_field.append(doc[field])
            self.indexed_docs[field] = data_field

    def fit(self):
        self.set_docs(self.document.docs)
        self.vectorizers = dict()
        self.dims = dict()
        for field in self.fields["index"]:
            data = self.indexed_docs[field]
            vectorizer = Vectorizer()
            vectorizer.set_docs(data)
            data = vectorizer.fit_transform()
            data = np.ascontiguousarray(data)
            self.indexed_docs[field] = data
            self.vectorizers[field] = vectorizer
            self.dims[field] = self.indexed_docs[field].shape[1]
    
        self.faiss_indices = dict()
        for field in self.fields["index"]:
            self.faiss_indices[field] = faiss.IndexFlatIP(self.dims[field])
            self.faiss_indices[field].add(self.indexed_docs[field])

    def search(self, query):
        self.start = time.time()
        query = Query(query)
        self.queries = query.queries
        self.score = dict()
        for field in self.fields["index"]:
            vectors = query.transform(self.vectorizers[field])
            matrix = np.array(vectors)
            D, I = self.faiss_indices[field].search(matrix, self.number_results)
            D, I = D[0], I[0]
            for i, d in zip(I, D):
                if i not in self.score:
                    self.score[i] = d
                else:
                    self.score[i] = min(self.score[i], d)
        return self.show()

    def show(self):
        scores = sorted(self.score.items(), key=operator.itemgetter(1))
        results = []
        for key, _ in scores[::-1]:
            doc = self.docs[key]
            for field in self.fields["show"]:
                print(doc[field].replace('_', ' '))      # Adjust cause of tokenize
            print("#" * 50)
            results.append(str(doc[self.primary_field]))
        results = {
            "ids" : results,
            "query" : self.queries,
            "search_time" : time.time() - self.start
        }
        return results
        