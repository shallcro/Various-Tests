import spacy
import os
import statistics
from collections import Counter
from tika import parser
from sys import argv
import tika
tika.TikaClientOnly = True


def print_results(results, label, f):
    print('\n\n\n{}:\n'.format(label))
    f.write('{} Entity Report:\n\n'.format(label))
    
    try:
        class_mean = statistics.median(sorted(set(list(results.values()))))
    except statistics.StatisticsError:
        print('\t\tNo results for this entity.')
        f.write('No results for this entity.\n')
        return
        
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
    #load English model. Small provides 
    nlp = spacy.load("en_core_web_sm")
    
    ship_dir = argv[1]
    barcode = argv[2]
    
    files_dir = os.path.join(ship_dir, barcode, 'files')
    metadata = os.path.join(ship_dir, barcode, 'metadata')
    reports_dir = os.path.join(metadata, 'reports')
    
    person_rpt = os.path.join(reports_dir, 'ner_people.txt')
    norp_rpt = os.path.join(reports_dir, 'ner_norp.txt')
    fac_rpt = os.path.join(reports_dir, 'fac_people.txt')
    org_rpt = os.path.join(reports_dir, 'org_people.txt')
    gpe_rpt = os.path.join(reports_dir, 'gpe_people.txt')
    loc_rpt = os.path.join(reports_dir, 'loc_people.txt')
    
    
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
            combined_text = ' '.join(text)
            
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

    for ls in [person, norp, fac, org, gpe, loc]:
        
        #tally the number of unique entities in each list.  Reconciling near matches or eliminating false positives would require too much human intervention
        tally = dict(Counter(ls))
        
        #sort the resulting dictionary so we can present results in descending order, with the most frequent first
        sorted_tally = {k: v for k, v in sorted(tally.items(), key=lambda item: item[1], reverse=True)}
        
        #for each list, assign label and open a file to write results
        if ls == person:
            label = 'PEOPLE'
            f = open(person_rpt, 'a', encoding='utf8')
            
        elif ls == norp:
            label = 'NATIONALITIES & POLITICAL/RELIGIOUS GROUPS'
            f = open(norp_rpt, 'a', encoding='utf8')
            
        elif ls == fac:
            label = 'FACILITIES'
            f = open(fac_rpt, 'a', encoding='utf8')
            
        elif ls == org:
            label = 'ORGANIZATIONS'
            f = open(org_rpt, 'a', encoding='utf8')
            
        elif ls == gpe:
            label = 'COUNTRIES, CITIES, STATES'
            f = open(gpe_rpt, 'a', encoding='utf8')
            
        elif ls == loc:
            label = 'OTHER LOCATIONS'
            f = open(loc_rpt, 'a', encoding='utf8')
        
        #call function to present results
        print_results(sorted_tally, label, f)
        
        f.close()


if __name__ == "__main__":
    main()

