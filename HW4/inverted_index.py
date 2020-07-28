
class Appearance:
    """
    Represents the appearance of a term in a given document, along with the
    frequency of appearances in the same one.
    """
    def __init__(self, docId, frequency):
        self.docId = docId
        self.frequency = frequency
        # self.prob = -1
        
    def __repr__(self):
        """
        String representation of the Appearance object
        """
        return str(self.__dict__)

    # def add_prob(self, doc_len):
    #     self.prob = self.frequency / doc_len

class Database:
    """
    In memory database representing the already indexed documents.
    """
    def __init__(self):
        self.db_index = dict()
        self.db_length = dict()
    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.__dict__)
    
    def get_index(self, doc_name):
        return self.db_index.get(doc_name, None)

    def add_index(self, doc_name, index):
        """
        Adds documents as a key and their index in the content list.
        """
        self.db_index[doc_name] = index

    def add_length(self, index, length):
        """
        Adds a document index as a key and its length to the DB.
        """
        self.db_length.update({index: length})

    def get_length(self, doc_name):
        return self.db_length[self.db_index[doc_name]]

    # def remove(self, document):
    #     """
    #     Removes document from DB.
    #     """
    #     return self.db.pop(document['id'], None)

class InvertedIndex:
    """
    Inverted Index class.
    """
    def __init__(self, db: Database):
        self.term_index = dict()
        self.db = db

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.db)
        
    def index_document(self, doc_id, document: list):
        """
        Process a given document, save it to the DB and update the index.
        """
        # terms in a document
        term_set = set(document)

        # # Remove punctuation from the text.
        # clean_text = re.sub(r'[^\w\s]','', document['text'])
        # terms = clean_text.split(' ')
        # appearances_dict = dict()
        # Dictionary with each term and the frequency it appears in the text.
        for term in term_set:
            term_frequency = document.count(term)
            appearance = Appearance(doc_id, term_frequency)
            if term in self.term_index.keys():
                self.term_index[term].append(appearance)
            else:
                self.term_index[term] = [appearance]
    
    def lookup_terms_freq(self, all_terms, doc_id):
        """
        Returns the dictionary of frequency of terms. 
        """
        term_freq = dict()
        for term in all_terms:
            val = self.term_index[term]
            for appearance in val:
                if appearance.docId == doc_id:
                    term_freq[term] = appearance.frequency
        return term_freq


def unigram(wordcount_dict, one_doc_length):
    """ Compute probabilities of words in one document, and return a dictionary of term probability. """
    wordprob_dict = {}
    word_instance = len(list(wordcount_dict.keys()))
    for word, wordcount in wordcount_dict.items():
        # prob = lidston_smoothing(wordcount, one_doc_length, word_instance, 0.5)
        prob = wordcount / one_doc_length
        wordprob_dict[word] = prob   
    return wordprob_dict 

def lidston_smoothing(wordcount, doc_length, word_instance, landa):
    """ Increase word count of each word by landa to avoid zero probability, and return the probability. """
    return (wordcount + landa)/(doc_length + word_instance * landa)

def word_instance_num(wordcount_dict, query: list):
    instance = len(list(wordcount_dict.keys()))
    for word in query:
        if word not in wordcount_dict.keys():
            instance += 1
    return instance

def smoothing_unigram(wordcount_dict, one_doc_length, query, landa):
    wordprob_dict = {}
    #word_instance = len(list(wordcount_dict.keys()))
    word_instance = word_instance_num(wordcount_dict, query)
    for word, wordcount in wordcount_dict.items():
        prob = lidston_smoothing(wordcount, one_doc_length, word_instance, landa)
        wordprob_dict[word] = prob   
    return wordprob_dict 


def interpolation(term, word_prob, background_model_prob, alpha):
    if word_prob == 0 and background_model_prob == 0:
        print("zero prob: ", term)
    return (1-alpha) * word_prob + (alpha) * background_model_prob




def modeling(wordcount_dict, one_doc_length, background_model, query_terms, word_instance):
    """ Compute the query likelihood score of one document and return the score. """
    wordprob_dict = smoothing_unigram(wordcount_dict, one_doc_length, query_terms, 0.00001)
    #word_instance = len(list(wordcount_dict.keys()))
    score = 1
    for term in query_terms:
        if term in wordprob_dict:
            interpolate_prob = interpolation(term, wordprob_dict[term], background_model[term], 0.5)
        else:
            prob = lidston_smoothing(0, one_doc_length, word_instance, 0.00001)
            interpolate_prob = interpolation(term, prob, background_model[term], 0.5)
        score = score * interpolate_prob
    return score

def query_likelihood(docword_count_dict, docs_length_dict, background_model, query_terms):
    rank = []
    for doc, freqs in docword_count_dict.items():
        word_instance = word_instance_num(freqs, query_terms)
        score = modeling(freqs, docs_length_dict[doc], background_model, query_terms, word_instance)
        rank.append([doc, score])
    rank.sort(key = lambda x: x[1], reverse = True)
    return rank
    
    


