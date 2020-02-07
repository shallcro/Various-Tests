import os

correct = 'C:/temp/20191010_correct.txt'
current = 'C:/temp/20191010_current.txt'

corr = []
curr = []

with open(correct, 'r') as f:
    for barcode in f.read().splitlines():
        corr.append(barcode)

with open(current, 'r') as f:
    for barcode in f.read().splitlines():
        curr.append(barcode)
        
for f in range(0, 12):
    cur_dir = os.path.join('Z:\\Ripstation', curr[f])
    cur_di = os.path.join(cur_dir, 'disk-image', '%s.iso' % curr[f])

    cor_di = os.path.join(cur_dir, 'disk-image', '%s.iso' % corr[f])
    
    os.rename(cur_di, cor_di)
    
    cor_dir = os.path.join('Z:\\Ripstation', corr[f])
    
    os.rename(cur_dir, cor_dir)