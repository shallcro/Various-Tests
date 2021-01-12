import shelve

myshelve = 'C:/temp/myshelve'

db = shelve.open(myshelve, writeback=True)

if not db.get('dict'):
    db['dict'] = {}
    
print(db['dict'])

db['dict']['name'] = input('Name: ')

db['dict']['age'] = input('Age: ')

db['dict']['band'] = input('Band: ')

print(db['dict'])

db.sync()