import os
from tika import parser
import tika
tika.TikaClientOnly = True
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.models import ldamodel
import spacy
from spacy.lemmatizer import Lemmatizer
from pprint import pprint

def lemmatizer(doc):
    # This takes in a doc of tokens from the NER and lemmatizes them. 
    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
    nlp = spacy.load("en_core_web_sm")
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)
    
def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    return doc
    
def main():
    
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
    nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

    # for word in STOP_WORDS:
        # lexeme = nlp.vocab[word]
        # lexeme.is_stop = True
    
    doc_list = []
    for root, dir, files in os.walk('C:/temp/minutes/0001'):
        for f in files:
            ner_target = os.path.join(root, f)
            print(ner_target)
            try:
                content = parser.from_file(ner_target)
            except UnicodeEncodeError:
                continue
            
            if 'content' in content:
                text = content['content']
            else:
                continue
            
            text = str(text).split()
            combined_text = ' '.join(t for t in text)
            
            #print(content['content'])
            docu = nlp(combined_text)
            
            doc_list.append(docu)
            #doc_list += doc
    
    print(doc_list)
    
    # Creates, which is a mapping of word IDs to words.
    words = corpora.Dictionary(doc_list)

    # Turns each document into a bag of words.
    corpus = [words.doc2bow(doc) for doc in doc_list]
    
    lda_model = ldamodel.LdaModel(corpus=corpus, id2word=words, num_topics=10, random_state=2, update_every=1, passes=10,  alpha='auto', per_word_topics=True)
    
    pprint(lda_model.print_topics(num_words=10))
    
    x=lda_model.show_topics(num_topics=10, num_words=8,formatted=False)
    topics_words = [(tp[0], [wd[0] for wd in tp[1]]) for tp in x]

    #Below Code Prints Topics and Words
    for topic,words in topics_words:
        print(str(topic)+ "::"+ str(words))
    print()

    #Below Code Prints Only Words 
    for topic,words in topics_words:
        print(" ".join(words))
    
if __name__ == "__main__":
    main()