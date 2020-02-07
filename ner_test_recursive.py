import spacy
import os
import statistics
from collections import Counter
from tika import parser
from sys import argv
import tika
tika.TikaClientOnly = True


def print_results(results, label, f, barcode):
    print('\n\n{}'.format(barcode))
    print('\n\t{}:\n'.format(label))
    
    f.write('\n\nBARCODE: {}\n'.format(barcode))
    f.write('\t{} Entity Report:\n'.format(label))
    
    try:
        class_mean = statistics.median(sorted(set(list(results.values()))))
        
    except statistics.StatisticsError:
        print('\t\tNo results for this entity.')
        f.write('No results for this entity.\n')
        return
    
    #set a boolean variable so we can check whether or not there were above-average results (and if they were printed)
    printed = False
    
    for k, v in results.items():
        #write all results to file
        f.write("{:>50} : {:<3}\n".format(k, v))
        
        #for appraisal purposes, present entities whose frequency is above average
        if v > class_mean:
            print("{:>50} : {:<3}".format(k, v))
            printed = True
            
    #if no entities have above-average frequency, print them all if there are 25 or fewer.  Otherwise, note that there are a large number and refer to report.
    if not printed:
        if len(results) <= 25:
            for k, v in results.items():
                print("{:>50} : {:<3}".format(k, v))
        else:
            print('A large number of statistically insignificant results; see raw data.')

def main():
    
    ship_dir = argv[1]
    person_rpt = os.path.join(ship_dir, 'ner_people.txt')
    norp_rpt = os.path.join(ship_dir, 'ner_norp.txt')
    fac_rpt = os.path.join(ship_dir, 'ner_fac.txt')
    org_rpt = os.path.join(ship_dir, 'ner_org.txt')
    gpe_rpt = os.path.join(ship_dir, 'ner_gpe.txt')
    loc_rpt = os.path.join(ship_dir, 'ner_loc.txt')    
    
    for barcode in [name for name in os.listdir(ship_dir) if os.path.isdir(os.path.join(ship_dir, barcode))]:
    
        files_dir = os.path.join(ship_dir, barcode, 'files')
        #metadata = os.path.join(ship_dir, barcode, 'metadata')
        #reports_dir = os.path.join(metadata, 'reports')
        
        #load English model. Small provides good enough NER while being faster than en_core_web_md
        nlp = spacy.load("en_core_web_sm")
        
        person = []
        norp = []
        fac = []
        org = []
        gpe = []
        loc = []
        
        for root, dirs, files, in os.walk(files_dir):
            for f in files:
                
                ner_target = os.path.join(root, f)
                
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
                            
                doc = nlp(combined_text)
                
                #add entities to appropriate list
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        person.append(ent.text) 
                    elif ent.label_ == 'NORP':
                        norp.append(ent.text)
                    elif ent.label_ == 'FAC':
                        fac.append(ent.text)
                    elif ent.label_ == 'ORG':
                        org.append(ent.text)
                    elif ent.label_ == 'GPE':
                        gpe.append(ent.text)
                    elif ent.label_ == 'LOC':
                        loc.append(ent.text)
                    else:
                        continue
        
        for ls in [person, org, gpe]:
            
            #tally the number of unique entities in each list and sort the resulting dictionary so we can present results in descending order, with the most frequent first.  Reconciling near matches or eliminating false positives would require too much human intervention
            
            if ls == person:
                label = 'PEOPLE'
                f = open(person_rpt, 'a', encoding='utf8')
                tally_person = {k: v for k, v in sorted(dict(Counter(person)).items(), key=lambda item: item[1], reverse=True)}
                print_results(tally_person, label, f, barcode)                
                
            elif ls == norp:
                label = 'NATIONALITIES & POLITICAL/RELIGIOUS GROUPS'
                f = open(norp_rpt, 'a', encoding='utf8')
                tally_norp = {k: v for k, v in sorted(dict(Counter(norp)).items(), key=lambda item: item[1], reverse=True)}
                print_results(tally_norp, label, f, barcode)
                
            elif ls == fac:
                label = 'FACILITIES'
                f = open(fac_rpt, 'a', encoding='utf8')
                tally_fac = {k: v for k, v in sorted(dict(Counter(fac)).items(), key=lambda item: item[1], reverse=True)}
                print_results(tally_fac, label, f, barcode)
                
            elif ls == org:
                label = 'ORGANIZATIONS'
                f = open(org_rpt, 'a', encoding='utf8')
                tally_org = {k: v for k, v in sorted(dict(Counter(org)).items(), key=lambda item: item[1], reverse=True)}
                print_results(tally_org, label, f, barcode)
                
            elif ls == gpe:
                label = 'COUNTRIES, CITIES, STATES'
                f = open(gpe_rpt, 'a', encoding='utf8')
                tally_gpe = {k: v for k, v in sorted(dict(Counter(gpe)).items(), key=lambda item: item[1], reverse=True)}
                print_results(tally_gpe, label, f, barcode)
                
            elif ls == loc:
                label = 'OTHER LOCATIONS'
                f = open(loc_rpt, 'a', encoding='utf8')
                tally_loc = {k: v for k, v in sorted(dict(Counter(loc)).items(), key=lambda item: item[1], reverse=True)}
                print_results(tally_loc, label, f, barcode)
                        
            f.close()

            


if __name__ == "__main__":
    main()

