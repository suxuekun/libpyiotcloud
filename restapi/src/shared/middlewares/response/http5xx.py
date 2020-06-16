from flask_api import status

BRAINTREE_TOKEN_ERROR = 'Can Not Get BrainTree Token'
responses = {
    BRAINTREE_TOKEN_ERROR:{
        'response':{'status': 'NG', 'message': BRAINTREE_TOKEN_ERROR},
        'status':status.HTTP_503_SERVICE_UNAVAILABLE,
    },
}