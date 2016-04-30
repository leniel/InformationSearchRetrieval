'''
    Author: Leniel Macaferi
    Date created: 4/30/2016
    Python Version: 3.5
'''

import configparser, os, logging, xml.etree.ElementTree as ET, nltk, csv
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

path = os.path.realpath('..')

# Configuring logger
logger = logging.getLogger('Exercise 1')
hdlr = logging.FileHandler(os.path.join(path, 'log/inverted_index_generator.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

logging.info("Inverted Index Generator started...")

logger.info('Started reading IIG config settings')

# Reading Config file settings
configPath = os.path.join(path, 'config/IIG.cfg')
config = configparser.ConfigParser()
config.readfp(open(configPath))

database_dir = config.get('Config', 'DATABASE_DIR')
read = config.get('Config', 'READ')
write = config.get('Config', 'WRITE')

logger.info('Finished reading IIG config settings... read: %s, write: %s', read, write)

files = read.split(',')

for i, file in enumerate(files):
    files[i] = file + ".xml"

dictionary = {}
allWords = []
stopwords = stopwords.words("english")

# Reading each file's records...
for file in files:

    with open(os.path.join(path, database_dir, file)) as f:
    
         root = ET.parse(f).getroot()
         
         # Extracting record information
         for child in root.iter('RECORD'):
         
             recordNum = int(child.find('RECORDNUM').text.strip())
             text = None
             
             if(child.find('ABSTRACT') is not None):
               text = child.find('ABSTRACT').text.upper()
             elif(child.find('EXTRACT') is not None):
               text = child.find('EXTRACT').text.upper()
             else:
               text = ""
               
             # Using NLTK to tokenize the text  
             tokenized = word_tokenize(text)
             
             # Removing stop words from text
             tokens = [t for t in tokenized if t not in stopwords]
             
             # Keeping only alphanumerical
             words = [t for t in tokens if t.isalpha()]
                        
             # Keep a dictionary with every Record and its associated terms\tokens\words  
             dictionary[recordNum] = words
             
             # Add this record's terms to the global terms list
             allWords.extend(words)
            
# Removing duplicates 
words = list(set(allWords))
       
result = {}

words = sorted(words)

for w in words:

    wordInRecords = []
        
    for record, text in sorted(dictionary.items()):

        # Count the ocurrences of the word within the record's text
        count = text.count(w)
    
        if count > 0:
           # Adding the same record as many times the word appears in that record
           for i in range(count):
               wordInRecords.append(record)       
    
    # Add to the result dictionary: the word as key and the list of records where it appears as value    
    result[w] = wordInRecords

# Create the output file
with open(os.path.join(path, write), 'w') as csv_file:
     
     writer = csv.writer(csv_file, delimiter=';')
     
     for w, records in sorted(result.items()):
        
         writer.writerow([w, records])

logger.info('Finished writing Inverted Index CSV file with #%s terms', len(result.items()))

logging.info("Inverted Index Generator finished")