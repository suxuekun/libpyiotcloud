This is for the front-end (mobile/web) developers.

SUMMARY:

    1. Plan:
        A. Get Plans                       - GET    /payment/plan/
        B. Get Plan Detail                 - GET    /payment/plan/{id}
        
    2. Subscription
        A. Get Subscriptions               - GET    /payment/subscription/
        B. Get Subscription Detail         - GET    /payment/subscription/{id}
       
    3. Promocode
        A. get user promocode              - GET    /payment/promocode/
        B. verify promocode                - POST   /payment/verify_promocode/
    
    
    4. AddOn # TODO
        A. get addOns                      - GET    /payment/addon/
        B. get addOn Details               - GET    /payment/addon/{id}
    5 Calculation Prorate
        A. prorate                         - GET    /payment/calc_prorate/
        
    6. payment setup and checkout
        A. get client token                - GET    /payment/client_token/
        B. checkout                        - POST   /payment/checkout
        
    7. billing address
        A. get billing address             - GET    /payment/billing_address
        A. create billing address          - POST   /payment/billing_address
        
        
    8. transaction history
        A. GET transactions                - GET    /payment/transaction/
        B. GET transactions Detail         - GET    /payment/transaction/{id}
        C. GET transaction reciept         - GET    /payment/transaction/reciept/
      
    x. cart # TODO replace payment check out
        A. get cartitems                   - GET    /payment/cartitem/
        B. get cartitem details            - GET    /payment/cartitem/{id}
        C. create cartItem                 - POST   /payment/cartitem/
        D. update cartItem                 - PUT    /payment/cartitem/{id}
        E. delete cartItem                 - DELETE /payment/cartitem/{id}
        F. checkout                        - POST   /payment/cart/checkout/

DETAIL:

    1. Plan:
        A. Get Plans
        - Request:
        GET: /payment/plan/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Reponse:
        { 
            'status': 'OK', 
            'data': true, 
            'plans': [
              {
                id:"id",
                name:"Free Plan",
                price:0,
                period:1, // every period month as one cycle ,1 = monthly 12 = yearly
                sms:5,
                notification:50,
                email:50,
                storage:50, // in MB
              },
              {...}
            ]
        }
        
      
        B. Get Plan Detail
        - Request:
        GET: /payment/plan/{id}
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Reponse:
        { 
            'status': 'OK', 
            'data': true, 
            'plan':{
                id:"id",
                name:"Free Plan",
                price:0,
                period:1, // every period month as one cycle ,1 = monthly 12 = yearly
                sms:5,
                notification:50,
                email:50,
                storage:50, // in MB
            } 
        }
