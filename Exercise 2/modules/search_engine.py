import configparser, os, csv, re, numpy, pickle, logging, time
from collections import OrderedDict
from scipy import spatial

class indexer:

    def __init__(self, terms, docs, matrix):
        self.terms = terms
        self.documents = docs
        self.matrix = matrix

class query:

    def __init__(self, query_number, query_text):
        self.query_number = query_number
        self.query_text = query_text

class document_similarity:

    def __init__(self, document, similarity):
        self.document = document
        self.similarity = similarity

    def add_rank(self, rank):
        self.rank = rank

class search_result:

    def __init__(self, query_number, result):
        self.query_number = query_number
        self.result = result

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
    search_results = []

    # Reading SE Config file settings
    configPath = os.path.join(path, '../config/SE.cfg')
    config = configparser.ConfigParser()
    config.readfp(open(configPath))

    logger.info("Reading SE.cfg")

    model = config.get("Config", "MODEL")
    queries_csv = config.get("Config", "QUERIES")
    results_csv = config.get("Config","RESULTS")
    
    # Reading IIG Config file settings
    configPath = os.path.join(path, '../config/IIG.cfg')
    config = configparser.ConfigParser()
    config.readfp(open(configPath))
    
    # Used to assing appropriate name to the generated .CSV file
    stemmer = config.getboolean('Config', 'STEMMER') # Stemmer config can be True or False

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
             queries.append(query(row[0], row[1]))

    logger.info("Calculating similarity distance")

    # Similarity calculation...
    for q in queries:
    
        # Getting query words/tokens
        text = q.query_text.split()

        # Creating a search vector as bigger as the number of terms indexed for the corpus database
        search_vector = numpy.zeros([len(indexer.terms)])
        
        for word in text:
        
            if word in indexer.terms:
               search_vector[indexer.terms.index(word)] = 1 # Each word found has weight = 1

        docs_similarities = []

        i = 0
        
        # Matrix rows = Terms
        # Matrix rows = Docs
        # For each column\document vector in the matrix...
        for document_vector in indexer.matrix.T:
        
            ''' Calculates the similarity using Cosine distance for each term/document vector given a search vector
            # spatial.distance.cosine computes the distance, not the similarity.
            # We must subtract the value from 1 to get the similarity.
            A similarity = 1 means both vectors are equal. '''
            similarity = 1 - spatial.distance.cosine(search_vector, document_vector)
         
            docs_similarities.append(document_similarity(indexer.documents[i], similarity))
            
            i += 1

        # Sorting by similarity: the greater the similarity the best is the match
        docs_similarities.sort(key = lambda x: x.similarity, reverse = True)

        i = 0
        
        for ds in docs_similarities:
        
            # Assigning a rank to the document
            if(ds.similarity > 0 and ds.similarity <= 1):
              ds.add_rank(i)
            else:
                 ds.add_rank(-1) # document does not satisfy the query and as such won't be ranked
            
            i+=
            
        sr = search_result(q.query_number, docs_similarities)
        
        search_results.append(sr)

    end_time = time.perf_counter()
    total_time = end_time - begin_time

    logger.info("Search Engine processed " + str(len(search_results) / total_time) + " queries per second")

    # Using Python ternary operator to assing appropriate name to the CSV file based on the use of Potter Stemmer
    results_CSV_name = (results_csv + "_with_stemmer" if stemmer else results_csv + "_without_stemmer") +  ".csv"

    logger.info("Potter Stemmer = %s", stemmer)
        
    logger.info("Writing to CSV file: " + results_CSV_name)

    # Writing to the output file
    with open(os.path.join(path, "../output", results_CSV_name), 'w', newline='') as csv_file:
         writer = csv.writer(csv_file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

         for sr in search_results:

             ordered_pairs = '['

             for result in sr.result:
                 if(result.rank != -1):
                   ordered_pairs += "(" + str(result.rank) + "," + str(result.document) +"," + str(result.similarity)+ "), "

             ordered_pairs += ']'
             
             writer.writerow([sr.query_number, ordered_pairs])
            
    logger.info('Search Engine finished')

main()