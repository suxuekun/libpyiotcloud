from flask_api import status

TOKEN_EXPIRE = 'Token Expire'
INVALID_AUTHORIZATION_HEADER = 'Invalid Authorization Header'
UNAUTHORIZED_ACCESS = 'Unauthorized Access'
BAD_REQUEST = 'Bad Request'
DATA_NOT_FOUND = 'Data Not Found'


responses = {
    BAD_REQUEST:{
        'response':{'status': 'NG', 'message': 'Bad Request'},
        'status':status.HTTP_400_BAD_REQUEST,
    },
    TOKEN_EXPIRE:{
        'response':{'status': 'NG', 'message': 'Token Expired'},
        'status':status.HTTP_401_UNAUTHORIZED,
    },
    INVALID_AUTHORIZATION_HEADER:{
        'response':{'status': 'NG', 'message': 'Invalid Authorization Header'},
        'status':status.HTTP_401_UNAUTHORIZED,
    },
    UNAUTHORIZED_ACCESS:{
        'response':{'status': 'NG', 'message': 'Unauthorized access'},
        'status':status.HTTP_401_UNAUTHORIZED,
    },
    DATA_NOT_FOUND:{
        'response':{'status': 'NG', 'message': 'Data Not Found'},
        'status':status.HTTP_404_NOT_FOUND,
    },

}