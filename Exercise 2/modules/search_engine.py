import configparser, os, csv, re, numpy, pickle, logging, time
from collections import OrderedDict
from scipy import spatial

class indexer:

    def __init__(self, terms, docs, matrix):
        self.terms = terms
        self.documents = docs
        self.matrix = matrix

class queryNumber_queryText:

    def __init__(self,queryNumber, queryText):
        self.queryNumber = queryNumber
        self.queryText = queryText

class document_similarity:

    def __init__(self, document, similarity):
        self.document = document
        self.similarity = similarity

    def add_ranking(self, ranking):
        self.ranking = ranking

class query_result:

    def __init__(self, queryNumber, results):
        self.queryNumber = queryNumber
        self.results = results

def main():

    path = os.path.dirname(__file__)

    # Configuring Logger
    logger = logging.getLogger('Exercise 2')
    logger.setLevel(logging.DEBUG)
    # Create handlers
    file_handler = logging.FileHandler(os.path.join(path, '../log/search_engine.log'), mode='w')
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # Add the handlers to the Logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Search Engine started...")

    queries = []
    queries_results = []

    # Reading Config file settings
    configPath = os.path.join(path, '../config/SE.cfg')
    config = configparser.ConfigParser()
    config.readfp(open(configPath))

    logger.info("Reading SE.cfg")

    model = config.get("Config", "MODEL")
    queries_csv = config.get("Config", "QUERIES")
    results_csv = config.get("Config","RESULTS")

    begin_time = time.perf_counter()

    logger.info("Reading vectorial model from file: " + model)

    # Loading the vectorial model
    with open(os.path.join(path, "../output/" + model), "rb") as input_file:
         indexer = pickle.load(input_file)

    logger.info("Reading queries CSV file: " + queries_csv)

    # Loading queries...
    with open(os.path.join(path, "../output/" + queries_csv)) as csv_file:
         spamreader = csv.reader(csv_file, delimiter=';', quotechar='|')
         
         for row in spamreader:
             queries.append(queryNumber_queryText(row[0], row[1]))

    logger.info("Calculating similarity distance")

    # Similarity calculation...
    for query in queries:
    
        text = query.queryText
        text = text.split()

        search_vector = numpy.zeros([len(indexer.terms)])
        
        for word in text:
        
            if word in indexer.terms:
               search_vector[indexer.terms.index(word)] = 1

        results = []

        i = 0
        
        for column in indexer.matrix.T:
        
            results.append(document_similarity(indexer.documents[i], (spatial.distance.cosine(search_vector, column))))
            
            i += 1

        results.sort(key=lambda x: x.similarity, reverse=False)

        i = 0
        
        for result in results:
        
            if(result.similarity > 0):
              result.add_ranking(i)
            else:
                 result.add_ranking(-1)
            
            i+= 1
            
        a = query_result(query.queryNumber, results)
        queries_results.append(a)

    end_time = time.perf_counter()
    total_time = end_time - begin_time

    logger.info("Search generated " + str(len(queries_results) / total_time) + " queries per second")

    logger.info("Writing to CSV file: " + results_csv)

    with open(os.path.join(path, "../output", results_csv), 'w', newline='') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for result in queries_results:

            ordered_pairs = '['

            for result_from_query in result.results:
                if(result_from_query.ranking != -1):
                    ordered_pairs += "(" + str(result_from_query.ranking) + "," + str(result_from_query.document) +"," + str(result_from_query.similarity )+ "), "

            ordered_pairs = ordered_pairs[:-2]
            ordered_pairs += ']'
            spamwriter.writerow([result.queryNumber,  ordered_pairs ])
            
    logger.info('Search Engine finished')

main()