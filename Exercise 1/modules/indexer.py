import configparser, os, csv, re, numpy, pickle, logging, time
from collections import OrderedDict

# Regex to return only strings\words that contain characters in ASCII from A to Z.
def special_match(strg, search=re.compile(r'[^A-Z]').search):
    return not bool(search(strg))

# TF\IDF calculation
def calculate_tf_idf(freqij,maxi,N,nj):
    return freqij/maxi * numpy.math.log(N/nj)

class indexer:

    def __init__(self, terms, docs, matrix):
        self.terms = terms
        self.documents = docs
        self.matrix = matrix

def main():

    path = os.path.realpath('..')

    # Configuring logger
    logger = logging.getLogger('Exercise 1')
    hdlr = logging.FileHandler(os.path.join(path, 'log/indexer.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)  
    logger.setLevel(logging.DEBUG)

    logger.info("Indexer started...")
    
    terms = []
    documents_csv = []
    documents = []
    
    # Reading Config file settings
    logger.info("Reading INDEXER.cfg")
        
    configPath = os.path.join(path, 'config/INDEXER.cfg')
    config = configparser.ConfigParser()
    config.readfp(open(configPath))

    read = config.get("Config", "READ")
    write = config.get("Config", "WRITE")

    logger.info ("Read " + read)

    begin_time = time.perf_counter()

    # Reading csv file that contains the inverted index list
    with open(os.path.join(path, read)) as csvfile:
    
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

    logger.info("Total index time " + str(total_time) + " for " + str(len(terms)) + " terms and " + str(len(documents)) + " documents" )
    logger.info("Indexer generated  " + str(len(terms) / total_time) + " terms per second")
    logger.info("indexer generated  " + str( len(documents) /total_time) + " documents per second" )

    logger.info("Writing serialized file with Pickle")
    
    # Output the result to be used later...
    with open(os.path.join(path, write), 'wb') as output:
        # Pickle file
        pickle.dump(index, output, pickle.HIGHEST_PROTOCOL)

    logger.info("Indexer finished")
                    
main()