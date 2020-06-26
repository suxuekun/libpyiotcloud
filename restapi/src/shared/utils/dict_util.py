def updates(a,*args):
    list(map(a.update,filter(lambda x:isinstance(x,dict),args)))

def check_contains(superset,subset):
    return all(item in superset.items() for item in subset.items())

def query_dict(query):
    def checker(superset):
        return check_contains(superset,query)
    return checker

def filter_list_of_dict(superset,query):
    return list(filter(query_dict(query), superset))

def list_to_index_dict(l,key):
    d = dict([(x.get(key),x) for x in l])
    return d
def pair_to_dict(l,spliter = " "):
    '''
    :param l: ['k1 v1','k2 v2','k3 v3',...] a list of string can be split by a spliter
    :param spliter: to split the string , default is " "
    :return: dict{k1:v1,k2:v2,k3:v3,...}
    '''
    return dict(map(lambda x: x.split(spliter), l))



if __name__ == "__main__":
    a = {'x':1}
    b = {'y':2}
    c = {'x':3}
    d = {'z':4}
    e = {'z':5}
    f = None
    updates(a,b,c,d,e,f)  # merge b,c,d to a , right prior , e override d
    print(a)

    res = check_contains(a,b)
    print (res)

    l = [
        {'i':1,'x': 1},
        {'i':2,'x': 2},
        {'i':3,'x': 3},
        {'i':4,'x': 4},
        {'i':5,'x': 5},
        {'i':6,'x': 1, 'y': 1},
        {'i':7,'x': 1, 'y': 2},
        {'i':8,'x': 1, 'y': 3},
        {'i':9,'x': 1, 'y': 4},
        {'i':10,'x': 1, 'y': 5},
    ]
    query = {'x':1}

    l2 = filter_list_of_dict(l,query)
    print (l2)

    d2 = list_to_index_dict(l,'i')
    print(d2)
