
class MainApp:
    def __init__(self):
        self.name = 'Mike Shallcross'
        self.age = 43

class Foo:
    def __init__(self):
        self.food = 'pizza'
        
class Worker(MainApp, Foo):
    def __init__(self):
        MainApp.__init__(self)
        Foo.__init__(self)
        
        self.job = 'Librarian'

class Bar:
    def __init__(self):
        self.car='Grand Caravan'

def main():

    ex = Worker()
    
    print(ex.name, ex.age, ex.job, ex.food, Bar().car)
    
if __name__ == "__main__":
    main()