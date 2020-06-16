def updates(a,*args):
    list(map(a.update,filter(lambda x:isinstance(x,dict),args)))



if __name__ == "__main__":
    a = {'x':1}
    b = {'y':2}
    c = {'x':3}
    d = {'z':4}
    e = {'z':5}
    f = None
    updates(a,b,c,d,e,f)  # merge b,c,d to a , right prior , e override d
    print(a)
