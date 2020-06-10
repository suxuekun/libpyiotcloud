from flask_api import status

TOKEN_EXPIRE = 'token expire'
INVALID_AUTHORIZATION_HEADER = 'Invalid authorization header'
UNAUTHORIZED_ACCESS = 'Unauthorized access'

responses = {
    TOKEN_EXPIRE:{
        'response':{'status': 'NG', 'message': 'Token expired'},
        'status':status.HTTP_401_UNAUTHORIZED,
    },
    INVALID_AUTHORIZATION_HEADER:{
        'response':{'status': 'NG', 'message': 'Invalid authorization header'},
        'status':status.HTTP_401_UNAUTHORIZED,
    },
    UNAUTHORIZED_ACCESS:{
        'response':{'status': 'NG', 'message': 'Unauthorized access'},
        'status':status.HTTP_401_UNAUTHORIZED,
    }
}