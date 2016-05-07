import configparser, os, csv, re, numpy, pickle, logging, time
from collections import OrderedDict

# Regex to return only strings\words that contain characters in ASCII from A to Z.
def special_match(strg, search=re.compile(r'[^A-Z]').search):
    return not bool(search(strg))

# TF\IDF calculation
def calculate_tf_idf(freqij, maxi, N, nj):
    return freqij/maxi * numpy.math.log(N/nj)

class indexer:

    def __init__(self, terms, docs, matrix):
        self.terms = terms
        self.documents = docs
        self.matrix = matrix

def main():

    path = os.path.dirname(__file__)
    
    # Configuring Logger
    logger = logging.getLogger('Exercise 2')
    logger.setLevel(logging.DEBUG)
    # Create handlers
    file_handler = logging.FileHandler(os.path.join(path, '../log/indexer.log'), mode='w')
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

    logger.info("Indexer started...")
    
    terms = []
    documents_csv = []
    documents = []
    
    # Reading Config file settings
    logger.info("Reading INDEXER.cfg")
        
    configPath = os.path.join(path, '../config/INDEXER.cfg')
    config = configparser.ConfigParser()
    config.readfp(open(configPath))

    read = config.get("Config", "READ")
    write = config.get("Config", "WRITE")

    logger.info ("Read " + read)

    begin_time = time.perf_counter()

    # Reading csv file that contains the inverted index list
    with open(os.path.join(path, "../output/" + read)) as csvfile:
    
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        
        for row in spamreader:
            
            # Only terms with 2 or more letters and that match the regex for A to Z
            if (len(row[0]) < 2 and special_match(row[0])):
                continue # Skip this term
                
            terms.append(row[0])
            text = eval('[' + row[1] + ']')
            documents_csv.append(text[0])

    for row in documents_csv:
        for number in row:
            if(number not in documents):
                documents.append(number)

    matrix = numpy.zeros((len(terms),len(documents)))
    normalized_matrix = numpy.zeros(((len(terms),max(documents) + 1)))

    logger.info ("Producing Weighted Matrix")

    i = 0
    
    for term_appearance in documents_csv:
    
        for document_number in term_appearance:
        
            j = documents.index(document_number)
            
            matrix[i][j] += 1
            
        i += 1

    N = len(documents)

    logger.info ("Calculating TF-IDF...")

    column_max = []
    j = len(matrix[0]) - 1
    
    while(j > -1):
    
        column_max.append(matrix[:, j].max())
        
        j -= 1

    i = 0
    
    for row in matrix:
    
        j=0

        nj = 0
        
        for column in row:
        
            if(column > 0):
            
                nj += 1

        for column in row:
        
            freqij = column

            maxi = column_max[j]
            
            if(freqij > 0):
            
                matrix[i][j] = calculate_tf_idf(freqij,maxi,N,nj)
                
            j += 1
            
        i+= 1

    index = indexer(terms, documents, matrix)

    end_time = time.perf_counter()
    total_time = end_time - begin_time
    terms_per_second = len(terms)/total_time
    docs_per_second = len(documents)/total_time

    logger.info("Total index time = " + str(total_time) + " second(s) for " + str(len(terms)) + " terms and " + str(len(documents)) + " documents" )
    logger.info("Indexer processed " + str(terms_per_second) + " terms per second")
    logger.info("indexer processed " + str(docs_per_second) + " documents per second" )

    logger.info("Writing serialized file with Pickle")
     
    # Output the result to be used later...
    with open(os.path.join(path, "../output", write), 'wb') as output:
        # Pickle file
        pickle.dump(index, output, pickle.HIGHEST_PROTOCOL)

    logger.info("Indexer finished")
                    
main()