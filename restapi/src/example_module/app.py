from example_module.routes import example_blueprint

'''

this is a example module of how to start work with
1 flask blueprint
2 flask-restful
3 middleware
4 blueprint.before_request

'''
class ExampleApp:
    def __init__(self, app,prefix="/example"):
        app.register_blueprint(example_blueprint, url_prefix=prefix)
        '''all apis with prefix (default is '/example')
        -GET      /test/id/
        -PUT      /test/id/
        -DELETE   /test/id/
        -POST     /test/
        -GET      /test/
  
        -GET      /bulk/id/
        -PUT      /bulk/id/
        -DELETE   /bulk/id/
        -POST     /bulk/
        -GET      /bulk/
        
        -GET      /raw/
        '''
