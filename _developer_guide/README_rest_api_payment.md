This is for the front-end (mobile/web) developers.

SUMMARY:

    1. Plan:
        A. Get Plans                       - GET    /payment/plan/
        B. Get Plan Detail                 - GET    /payment/plan/{id}/
        
    2. Subscription
        A. Get Subscriptions               - GET    /payment/subscription/
        B. Get Subscription Detail         - GET    /payment/subscription/{id}/
       
    3. Promocode
        A. get user promocodes             - GET    /payment/promocode/
        B. get user promocode              - GET    /payment/promocode/{id}/
        C. verify promocode                - POST   /payment/verify_promocode/
        
    4. AddOn # TODO
        A. get addOns                      - GET    /payment/addon/
        B. get addOn Details               - GET    /payment/addon/{id}
        
    5 Calculation Prorate
        A. prorate                         - POST   /payment/prorate/calc/
        
    6. payment setup and checkout
        A. get client token                - GET    /payment/client_token/
        B. checkout                        - POST   /payment/checkout/
        
    7. billing address
        A. get billing address             - GET    /payment/billing_address/
        B. create billing address          - POST   /payment/billing_address/
        C. update billing address          - PUT    /payment/billing_address/
        
    8. transaction history
        A. GET transactions                - GET    /payment/transaction/{filter}
        B. GET transactions Detail         - GET    /payment/transaction/{id}/
        C. GET transaction reciept         - GET    /payment/transaction/reciept/{id}
      
    x. cart # TODO replace payment check out
        A. get cartitems                   - GET    /payment/cartitem/
        B. get cartitem details            - GET    /payment/cartitem/{id}/
        C. create cartItem                 - POST   /payment/cartitem/
        D. update cartItem                 - PUT    /payment/cartitem/{id}/
        E. delete cartItem                 - DELETE /payment/cartitem/{id}/
        F. checkout                        - POST   /payment/cart/checkout/

DETAIL:
      
    1. Plan:
        A. Get Plans
        - Request:
        GET: /payment/plan/
        headers: {'Content-Type': 'application/json'}
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
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
        GET: /payment/plan/{id}/
        headers: {'Content-Type': 'application/json'}
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
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

    2. Subscription
        A. Get Subscriptions 
        - Request:
        GET: /payment/subscription/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
            'subscriptions':[
                {
                    id:"id",
                    device_id:"id",
                    device_name:"device name",
                    current:{
                        plan:{
                            name:"Free Plan",
                            price:0,
                            period:1, // every period month as one cycle ,1 = monthly 12 = yearly
                            sms:5,
                            notification:50,
                            email:50,
                            storage:50, // in MB
                        },
                        usage:{
                            sms:1,
                            notification:20,
                            email:10,
                            storage:20, // in MB
                        }
                    },
                    next:{
                        plan:{
                            name:"Free Plan",
                            price:0,
                            period:1, // every period month as one cycle ,1 = monthly 12 = yearly
                            sms:5,
                            notification:50,
                            email:50,
                            storage:50, // in MB
                        }
                    },
                    
                },
                {...}
            ] 
        }
        
        B. Get Subscription Detail
        - Request:
        GET: /payment/subscription/{id}/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
            'subscription':{
                id:"id",
                device_id:"id",
                device_uuid:"device name",
                status: int // 0 normal , 1 canceled , 2 downgraded
                current:{ // current month subscription
                    plan:{
                        name:"Free Plan",
                        price:0,
                        period:1, // every period month as one cycle ,1 = monthly 12 = yearly
                        sms:5,
                        notification:50,
                        email:50,
                        storage:50, // in MB
                    },
                    usage:{
                        sms:1,
                        notification:20,
                        email:10,
                        storage:20, // in MB
                    }
                },
                next:{ // if status != 0  
                    plan:{
                        name:"Free Plan",
                        price:0,
                        period:1, // every period month as one cycle ,1 = monthly 12 = yearly
                        sms:5,
                        notification:50,
                        email:50,
                        storage:50, // in MB
                    }
                },    
            }
        }

    3. Promocode
        A. get user promocodes
        - Request:
        GET: /payment/promocode/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
            'promocodes':[
                {
                    id:"id",
                    code:string,
                    promo:{
                        id:'',
                        name:'10% off for first month',
                        type:'discount',// Choice('discount','addOn')
                        period:1,
                        value: 10   // discount percentage  
                    },
                },
                {// current no addOn type yet
                    id:"id",
                    code:string,//promocode string
                    promo:{
                        id:'',
                        name:'free xx addOn for one month',
                        type:'discount',// Choice('discount','addOn')
                        period:1,
                        value: 1   // addOn id
                    },
                     
                },
                {...}
            ] 
        }
        
        B. get user promocodes
        - Request:
        GET: /payment/promocode/{id}/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
            'promocode':{
                id:"id",
                code:string,
                promo:{
                    id:'',
                    name:'10% off for first month',
                    type:'discount',// Choice('discount','addOn')
                    period:1,
                    value: 10   // discount percentage  
                },
            }
        }
        
        C. verify promocode
        - Request:
        POST: /payment/verify_promocode/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data: { 'code': string }
        - Response:
        { 
            'status': 'OK', 
            'message': string, 
            'promocode':{
                id:"id",
                code:string,
                promo:{
                    id:'',
                    name:'10% off for first month',
                    type:'discount',// Choice('discount','addOn')
                    period:1,
                    value: 10   // discount percentage  
                },
            }
        }

    4. AddOn # TODO

    5. Calculation Prorate
        A. prorate 
        - Request:
        POST: /payment/prorate/calc/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data: { // current PLAN id , and change to PLAN id
            current: 2,
            change: 4 ,
            promocode: 'promocode', // if have
        }
        - Response:
        {
            'status': 'OK', 
            'message': string,
            'remaining_days': 15// days left
            'total_days': 31 // total days of month
            "prorate": "38.67",
            "discount": "1.33",
            "gst":0.07 // 7%
        }

    6. payment setup and checkout
        A. get client token  
        // client token is a one time token that client side get from backend side
        // client side use this token to get a one time nonce from braintree 
        - Request:
        GET: /payment/client_token/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "token": string,
        }
        
        B. checkout
        - Request:
        POST: /payment/checkout/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:{
            'nonce':string,
            'devices':[
                {
                    'id':'device_id',
                    'plan_id':'new_plan_id',
                    'promocode':'promocode', // if have else null
                    'addOns':[// TODO // if have else null
                        {
                            'id':'addOn_id',
                            'other_attr':'other_attr',//TODO
                        }
                    ]
                },
                {...} // can have more than one changes , so this api can apply one or more changes on upgrade / downgrade / cancel / recover 
            ]
        }
        - Response:
        {
            'status': 'OK', 
            'message': string,
        }   

    7. billing address
        A. get billing address  
        - Request:
        GET: /payment/billing_address/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "billing_address": {
                name:'',
                billing_address:'',
                country:'',
                city:'',
                postal:'',
                region:'',
            },
        }
        // or have info
        {
            'status': 'OK', 
            'message': string,
            "billing_address": {
                name:'xxx',
                billing_address:'somewhere in singapore',
                country:'Singapore',
                city:'Singapore',
                postal:'222222',
                region:'Singapore',
            },
        }
        
        B. create billing address 
        - Request:
        POST: /payment/billing_address/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:{ // all keys needed, if blank or no such key , will set to default or blank if allowed; if not allow blank for the key ,will fail
            name:'xxx',
            billing_address:'somewhere in singapore',
            country:'Singapore',
            city:'Singapore',
            postal:'222222',
            region:'Singapore',
        }
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "billing_address": {
                name:'xxx',
                billing_address:'somewhere in singapore',
                country:'Singapore',
                city:'Singapore',
                postal:'222222',
                region:'Singapore',
            },
        }
        
        C. update billing address 
        - Request:
        PUT: /payment/billing_address/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:{// put can have only changed lines , the key not in the data will keep the same
            billing_address:'somewhere else in singapore',
            postal:'555555',
        }
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "billing_address": {
                name:'xxx',
                billing_address:'somewhere else in singapore',
                country:'Singapore',
                city:'Singapore',
                postal:'555555',
                region:'Singapore',
            },
        }

    8. transaction history
        A. GET transactions 
        - Request:
        GET: /payment/transaction/{filter} // e.g. /payment/transaction/?start=2019-01-01&end=2020-01-01
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "transactions": [
                {
                    'id':'id',
                    'remark':'remark',
                    'date': string,//payment date timestamp
                    'device_id':'device_id',// if have
                    'payment_type':'',
                    'account':string,//paypal transaction id or other payment account if have
                    'recurring':true,
                    'start':string, // if recurring , the period start date timestamp
                    'end':string, // if recurring , the period end date timestamp string
                },
                {...} // more transactions
            ]
        }
        B. GET transactions 
        - Request:
        GET: /payment/transaction/{id}/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "transaction": {
                'id':'id',
                'remark':'remark',
                'date':string,//payment date timestamp
                'device_id':'device_id',// if have
                'payment_type':'',
                'account':string,//paypal transaction id or other payment account if have
                'recurring':true,
                'start':string, // if recurring , the period start date timestamp
                'end':string, // if recurring , the period end date timestamp string
            }
        }

        C. GET transaction reciept #TODO
                 


