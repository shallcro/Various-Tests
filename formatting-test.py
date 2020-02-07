import textwrap

dc = {'really, really, really, really, really, really, really looooooooooooooooong': 2, 'short': 1, 'medium length key' : 134, 'pretty kinda sorta long but not as long as others' : 56}

with open('C:/temp/textwrap.txt', 'w') as f:
    for k in dc.keys():
        if len(k) < 30:
            diff = 30 - len(k)
            spaces = len(k) + diff
            value = k.rjust(spaces, ' ')
            #print('Too short:\noriginal: {}\nLength: {}\nNew value: *{}*\n\n\n'.format(k, len(k), value))
        elif len(k) > 30:
            content = textwrap.wrap(k, 30)
            for i, c in enumerate(content):
                if len(c) < 30:
                    diff = 30 - len(c)
                    spaces = len(c) + diff
                    content[i] = c.rjust(spaces, ' ')
            value = '\n'.join(content)
            #print('Too long:\noriginal: {}\nLength: {}\nNew value: *{}*\n\n\n'.format(k, len(k), temp_item))
        else:
            value = k
            #print('Just right:\noriginal: {}\nLength: {}\nNew value: *{}*\n\n\n'.format(k, len(k), value))
                
        f.write("{} : {}\n\n".format(value, dc[k]))