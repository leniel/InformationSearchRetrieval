import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

text =  """ A CISTERNAE The significance of addition Pseudomonas aeruginosa infection in the
respiratory tract of 9 cystic fibrosis patients have been studied addition
by means of immunoelectrophoretical analysis of patients' sera for
the number of precipitins against Pseudomonas aeruginosa and the CISTERNAE
concentrations of 16 serum proteins.  A In addition, the clinical addition and
radiographical status of the lungs have been evaluated using 2
scoring systems.  Precipitins against Pseudomonas aeruginosa were
demonstrated in all sera, the maximum number in one serum was 22.
The concentrations of 12 of the serum proteins CISTERNAE were significantly
changed compared with matched control persons.  Notably IgG and IgA
were elevated and the "acute phase proteins" were changed, the
latter suggesting active tissue damage.  The concentrations of 3 of
the acute phase proteins, notably haptoglobin, were correlated to
the number of precipitins suggesting that the respiratory tract
infection in patients with many precipitins is accompanied by more
tissue damage than the infection in patients with few precipitins.
The results indicate no protective value of the many precipitins on
the tissue of the respiratory tract."""

# Using NLTK to tokenize the text  
tokenized = set(word_tokenize(text)) #set removes duplicates