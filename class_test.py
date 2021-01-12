
class MyObj:
    def __init__(self):
        self.name='taco'
        self.age=23
        
    def do_stuff(self):
        new = NewObj(self)
        new.print_name()
        
class NewObj:
    def __init__(self, obj):
        self.obj = obj
    
    def print_name(self):
        print('Object: ', self.obj)
        print('Type: ', type(self.obj))
        print(self.obj.__class__.__name__)
        
def main():

    me = MyObj()
    me.do_stuff()
    
if __name__ == "__main__":
    main()