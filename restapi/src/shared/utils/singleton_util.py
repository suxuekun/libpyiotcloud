class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


if __name__ == "__main__":
    class Base():
        def __call__(self):
            print(self.name)
        @property
        def name(self):
            return self._name

        @name.setter
        def name(self,name):
            self._name = name

    class A(Base,metaclass=Singleton):
        def __init__(self,name:str):
            self.name = name

        @Base.name.setter
        def name(self,name):
            self._name = "class A:"+name

    class AChild(A):
        pass


    class B(Base):
        def __init__(self,name:str):
            self.name = name

        @Base.name.setter
        def name(self, name):
            self._name = "class B:" + name

    a = A(' i am a')
    b = B(' i am b')
    print (a.name)
    print (b.name)

    c = A(' i am c')
    d = B(' i am d')
    print ('a==c',id(a) == id(c),'c is a! no __init__ called again') # still A
    c.name = ' i am c'
    print ('a==c',id(a) == id(c),'but can set attr later with c')

    d.name = ' i am d'
    print ('b==d',id(b) == id(d),'b is not d, but a,b,c,d all child class of Base , a = c is singleton, b!=d')

    a_child = AChild(' i am a child')
    a_child_2 = AChild( 'i am a child 2')
    print ('a child == a child 2',id(a_child) == id(a_child_2),' just one child!!!, child also singleton')






