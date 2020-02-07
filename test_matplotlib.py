import matplotlib.pyplot as plt
import numpy as np

def absolute_value(val):
    a  = numpy.round(val/100.*sizes.sum(), 0)
    return a
def func(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:d} hits".format(absolute)

def main():

    labels = ['Python', 'C++', 'Ruby', 'Java', 'Fortran', 'Basic', 'Foo', 'Bar']
    sizes = [215, 130, 245, 210, 90, 400, 257, 37]
    
    print(type(labels))
    
    #colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    #explode = (0.1, 0, 0, 0)  # explode 1st slice
    #plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.pie(sizes, labels=labels, autopct=lambda pct: func(pct, sizes))
    plt.axis('equal')
    plt.savefig('C:/temp/plot7.png')
    
if __name__ == "__main__":
    main()