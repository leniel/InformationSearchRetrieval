import configparser, os, codecs, re, csv, logging, time
from collections import OrderedDict
from lxml import etree as ET
from xml.dom import minidom

# Class used to read multiple "READ" instructions from the config file
class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict,self).__setitem__(key, value)

class querynum_querytext:

    def __init__(self,querynum,querytext):
        self.querynum = querynum
        self.querytext = querytext

class document_vote:

    def __init__(self,document,vote):
        self.document = document
        self.vote = vote

class querynum_parlist:

    def __init__(self,querynum):
        self.querynum = querynum
        self.querylist = []

class querynum_item_vote_list:

    def __init__(self, querynum,item_vote_list):
        self.querynum = querynum
        self.item_vote_list = item_vote_list

def main():

    path = os.path.realpath('..')

    # Configuring logger
    logger = logging.getLogger('Exercise 1')
    hdlr = logging.FileHandler(os.path.join(path, 'log/query_processor.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)  
    logger.setLevel(logging.DEBUG)
    
    logger.info("Query Processor started...")

    # Reading Config file settings
    config = configparser.RawConfigParser(strict=False, dict_type=MultiOrderedDict)

    logger.info("Reading QP.cfg")

    config.read([os.path.join(path, 'config/QP.cfg')])
    
    database_dir = config.get('Config', 'DATABASE_DIR')
    read = config.get("Config", "READ");
    queries = config.get("Config", "QUERIES");
    expected = config.get("Config", "EXPECTED");

    f = codecs.open(os.path.join(path, database_dir[0], 'cfcquery-2.dtd'))
    dtd = ET.DTD(f)

    row_query = []
    row_expected = []

    logger.info("Started reading XML")

    begin_time = time.perf_counter()
      
    for input in read:
       
        input_path = os.path.join(path, database_dir[0], input)
                  
        root = ET.parse(input_path)

        if(dtd.validate(root)):
          logger.info("Reading " + input + " XML file")

          xmldoc = minidom.parse(input_path)
          query_list = xmldoc.getElementsByTagName('QUERY')
            
          for q in query_list:
              querynum = q.getElementsByTagName('QueryNumber')
              querynum = int(querynum[0].firstChild.nodeValue)
              querytextnode = q.getElementsByTagName('QueryText')
              querytext = querytextnode[0].firstChild.nodeValue
              querytext = querytext.upper()
              querytext = re.sub('[^A-Z\ \']+', " ", querytext)
              row_query.append(querynum_querytext(querynum, querytext))

              record_list = q.getElementsByTagName('Records')
                
              for r in record_list:
                  item_votes_list = []
                  query_list = r.getElementsByTagName('Item')
                    
                  for i in query_list:
                      item_document = i.firstChild.nodeValue
                      score = i.getAttribute("score")
                      item_votes = 0
                        
                      for s in range(len(score)):
                        
                          if(score[s]) != '0':
                            item_votes += 1
                        
                      item_votes_list.append((int(item_document),item_votes))
                        
              row_expected.append(querynum_item_vote_list(querynum,item_votes_list))
        else:
             logger.info(input + " XML file didn't pass DTD validation")

             print(dtd.error_log.filter_from_errors())

    end_time = time.perf_counter()
    total_time = end_time - begin_time

    logger.info("Inverted list generated " + str(len(read) / total_time) + " documents per second")
    
    logger.info("Writing to CSV file")

    with open(os.path.join(path, queries[0]), 'w', newline='') as csvfile:
         spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
         for row in row_query:
             spamwriter.writerow([row.querynum,row.querytext])

    with open(os.path.join(path, expected[0]), 'w', newline='') as csvfile:
         spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
         
         for row in row_expected:
             spamwriter.writerow([row.querynum, row.item_vote_list])

    logger.info("Query Processor finished")

main()