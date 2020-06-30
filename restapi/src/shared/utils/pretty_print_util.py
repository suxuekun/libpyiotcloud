import pprint
pp = pprint.PrettyPrinter(indent=4)
DEBUG_MODE = True
def pretty_print(*args,**kwargs):
    return pp.pprint(*args,**kwargs)

def debug_print(pretty=True,*args,**kwargs):
    if not DEBUG_MODE:
        return
    if pretty:
        pretty_print(*args,**kwargs)
    else:
        print(*args,**kwargs)

