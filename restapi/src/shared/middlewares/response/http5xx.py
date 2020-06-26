from flask_api import status

BRAINTREE_TOKEN_ERROR = 'Can Not Get BrainTree Token'
BRAINTREE_CONNECTION_ERROR = 'Can Not Connect to BrainTree'

responses = {
    BRAINTREE_TOKEN_ERROR:{
        'response':{'status': 'NG', 'message': BRAINTREE_TOKEN_ERROR},
        'status':status.HTTP_503_SERVICE_UNAVAILABLE,
    },
    BRAINTREE_CONNECTION_ERROR:{
        'response':{'status': 'NG', 'message': BRAINTREE_CONNECTION_ERROR},
        'status':status.HTTP_503_SERVICE_UNAVAILABLE,
    },

}