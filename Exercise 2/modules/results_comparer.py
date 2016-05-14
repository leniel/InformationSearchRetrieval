import numpy, numpy, os, csv, logging
from math import log
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score

path = os.path.dirname(__file__)

def precision(expected, found):

    tp = 0 # true positives
    fp = 0 # false positives
    
    for doc in found:   
        if doc in expected:
           tp += 1          
        else:
           fp += 1

    p = tp / (tp + fp) # Total of relevant docs retrieved (true positives) / total retrieved by the search engine
    
    return p

def recall(expected, found):

    tp = 0
    
    for doc in found:
        if doc in expected:
           tp += 1

    rec = tp / len(expected) # Total of relevant docs retrieved (true positives) / total relevant docs
    
    return rec

def F1(precision, recall):

    return 2 * ((precision * recall) / (precision + recall))

def average(array):

    if len(array) == 0:
       return 0
    
    return sum(array) / len(array)

class result:

    def __init__(self, position, docs):
        self.position = position
        self.docs = docs

def compare(expected, search_result, stemmer = False):

    docs_expected = []
    docs_found = []
    
    for e in expected:
        
        arr = []
        
        for doc in e.docs:
            arr.append(doc[0])
        
        docs_expected.append(arr)

    for sr in search_result:
        
        arr = []
        
        for doc in sr.docs:
        
            similarity = float(doc[2])
            
            # Considering that the search engine retrieves only docs with a similirity > 0
            if(similarity > 0):
              arr.append(doc[1])
        
        docs_found.append(arr)

    number_of_queries = len(docs_found)

    # Arrays
    precision_10_arr = []
    precision_arr = []
    recall_arr = []
    recall_10_arr = []
    f1_arr = []
    dcg_arr = []
    ndcg_arr = []

    # Arrays to store 11 points for Precision Recall chart
    chart_p1 = []
    chart_p2 = []
    chart_p3 = []
    chart_p4 = []
    chart_p5 = []
    chart_p6 = []
    chart_p7 = []
    chart_p8 = []
    chart_p9 = []
    chart_p10 = []
    chart_p11 = []

    # For each query let's calculate the metrics...
    for i in range(0, number_of_queries):
        
        precision_10 = precision(docs_expected[i], docs_found[i][:10])
        precision_10_arr.append(precision_10)
        
        p = precision(docs_expected[i], docs_found[i])
        precision_arr.append(p)
        
        recall_10 = recall(docs_expected[i], docs_found[i][:10])
        recall_10_arr.append(recall_10)      
        
        rec = recall(docs_expected[i], docs_found[i])
        recall_arr.append(rec)
       
        f1 = F1(p, rec)        
        f1_arr.append(f1)

        if rec > 0 and rec < 0.05:
            chart_p1.append(p)
        if rec > 0.05 and rec < 0.15:
            chart_p2.append(p)
        if rec > 0.15 and rec < 0.25:
            chart_p3.append(p)
        if rec > 0.25 and rec < 0.35:
            chart_p4.append(p)
        if rec > 0.35 and rec < 0.45:
            chart_p5.append(p)
        if rec > 0.45 and rec < 0.55:
            chart_p6.append(p)
        if rec > 0.55 and rec < 0.65:
            chart_p7.append(p)
        if rec > 0.65 and rec < 0.75:
            chart_p8.append(p)
        if rec > 0.75 and rec < 0.85:
            chart_p9.append(p)
        if rec > 0.85 and rec < 0.95:
            chart_p10.append(p)
        if rec > 0.95:
            chart_p11.append(p)

    # Calculating averages... 
    chart_p1 = average(chart_p1)
    chart_p2 = average(chart_p2)
    chart_p3 = average(chart_p3)
    chart_p4 = average(chart_p4)
    chart_p5 = average(chart_p5)
    chart_p6 = average(chart_p6)
    chart_p7 = average(chart_p7)
    chart_p8 = average(chart_p8)
    chart_p9 = average(chart_p9)
    chart_p10 = average(chart_p10)
    chart_p11 = average(chart_p11)
    
    # Report.txt text file
    text_file = open(os.path.join(path, "../output", "report.txt"), "a" if stemmer else "w")
    
    text_file.write("With Potter Stemmer:\n" if stemmer else "Without Potter Stemmer:\n")
    text_file.write("Precision@10: " + str(average(precision_10_arr)) + "\n")
    text_file.write("MAP: " + str(average(precision_arr)) + "\n")
    text_file.write("F1: " + str(average(f1_arr)) + "\n\n")
      
    text_file.close()
    
    csv_name = ("11points_with_stemmer" if stemmer else "11points_without_stemmer") +  ".csv"

    with open(os.path.join(path, "../output", csv_name), 'w', newline = '') as _11points_CSV:
         writer = csv.writer(_11points_CSV, delimiter = ';', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
         writer.writerow([0  , chart_p1])
         writer.writerow([0.1, chart_p2])
         writer.writerow([0.2, chart_p3])
         writer.writerow([0.3, chart_p4])
         writer.writerow([0.4, chart_p5])
         writer.writerow([0.5, chart_p6])
         writer.writerow([0.6, chart_p7])
         writer.writerow([0.7, chart_p8])
         writer.writerow([0.8, chart_p9])
         writer.writerow([0.9, chart_p10])
         writer.writerow([1.0, chart_p11])

def main():

    # Configuring Logger
    logger = logging.getLogger('Exercise 2')
    logger.setLevel(logging.DEBUG)
    # Create handlers
    file_handler = logging.FileHandler(os.path.join(path, '../log/results_comparer.log'), mode = 'w')
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
    
    logger.info("Results Comparer started...")
    
    expected = []
    results_without_stemmer = []
    results_with_stemmer = []

    # Reading expected and results CSV files
    with open(os.path.join(path, "../output/expected.csv")) as expected_CSV:
         reader = csv.reader(expected_CSV, delimiter = ';', quotechar = '|')
         for row in reader:
             expected.append(result(row[0], eval(row[1])))

    logger.info("Read expected.csv file")
        
    with open(os.path.join(path, "../output/results_without_stemmer.csv")) as results_CSV:
         reader = csv.reader(results_CSV, delimiter = ';', quotechar = '|')
         for row in reader:
             results_without_stemmer.append(result(row[0], eval(row[1])))
             
    logger.info("Read results_without_stemmer.csv file")
    
    with open(os.path.join(path, "../output/results_with_stemmer.csv")) as results_CSV:
         reader = csv.reader(results_CSV, delimiter = ';', quotechar = '|')
         for row in reader:
             results_with_stemmer.append(result(row[0], eval(row[1])))
    
    logger.info("Read results_with_stemmer.csv file")
             
    compare(expected, results_without_stemmer)
    compare(expected, results_with_stemmer, True)
    
    logger.info("Results Comparer finished")
    
main()