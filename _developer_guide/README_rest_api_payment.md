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
        C. cancel subscription             - pOST   /payment/cancel_subscription/
        
    7. billing address
        A. get billing address             - GET    /payment/billing_address/
        B. create billing address          - POST   /payment/billing_address/
        
    8. transaction history
        A. GET transactions                - GET    /payment/transaction/{filter}
        B. GET transactions Detail         - GET    /payment/transaction/{id}/
      
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
          "status": "OK",
          "message": "",
          "data": [
            {
              "_id": "Free",
              "createdAt": "1592538065",
              "modifiedAt": "1592538065",
              "sms": "0",
              "email": "30",
              "notification": "100",
              "storage": "0.05",
              "name": "PlanA",
              "price": "0.00",
              "bt_plan_id": "Free"
            },
            {
              "_id": "Basic10",
              "createdAt": "1592538065",
              "modifiedAt": "1592538065",
              "sms": "0",
              "email": "100",
              "notification": "1000",
              "storage": "1",
              "name": "PlanB",
              "price": "10.00",
              "bt_plan_id": "Basic10"
            },
            {
              "_id": "Pro30",
              "createdAt": "1592538065",
              "modifiedAt": "1592538065",
              "sms": "0",
              "email": "1000",
              "notification": "100000",
              "storage": "3",
              "name": "PlanC",
              "price": "30.00",
              "bt_plan_id": "Pro30"
            },
            {
              "_id": "Enterprise50",
              "createdAt": "1592538065",
              "modifiedAt": "1592538065",
              "sms": "0",
              "email": "10000",
              "notification": "1000000",
              "storage": "10",
              "name": "PlanD",
              "price": "50.00",
              "bt_plan_id": "Enterprise50"
            }
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
            'data':{
              "_id": "Free",
              "createdAt": "1592538065",
              "modifiedAt": "1592538065",
              "sms": "0",
              "email": "30",
              "notification": "100",
              "storage": "0.05",
              "name": "PlanA",
              "price": "0.00",
              "bt_plan_id": "Free"
            },
        }

    2. Subscription
        A. Get Subscriptions 
        - Request:
        GET: /payment/subscription/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
          "status": "OK",
          "message": "",
          "data": [
            {
              "_id": "5eec927aa7053179739ac852",
              "username": "su-org.1592316898",
              "deviceid": "PH80XXRR0616207E",
              "devicename": "G1",
              "status": "normal",
              "draft_status": false,
              "current": {
                "_id": null,
                "start": null,
                "end": null,
                "sms": "0",
                "email": "0",
                "notification": "0",
                "storage": "0",
                "plan": {
                  "_id": "Free",
                  "createdAt": "1592533498",
                  "modifiedAt": "1592533498",
                  "sms": "0",
                  "email": "30",
                  "notification": "100",
                  "storage": "0.05",
                  "name": "PlanA",
                  "price": "0.00",
                  "bt_plan_id": "Free"
                },
                "bt_sub": null
              },
              "next": {
                "_id": null,
                "plan": {
                  "_id": "Free",
                  "createdAt": "1592533498",
                  "modifiedAt": "1592533498",
                  "sms": "0",
                  "email": "30",
                  "notification": "100",
                  "storage": "0.05",
                  "name": "PlanA",
                  "price": "0.00",
                  "bt_plan_id": "Free"
                },
                "bt_sub": null
              },
              "draft": null
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
            'data':{
                      "_id": "5eec927aa7053179739ac852",
                      "username": "su-org.1592316898",
                      "deviceid": "PH80XXRR0616207E",
                      "devicename": "G1",
                      "status": "normal",
                      "draft_status": false,
                      "current": {
                        "_id": null,
                        "start": null,
                        "end": null,
                        "sms": "0",
                        "email": "0",
                        "notification": "0",
                        "storage": "0",
                        "plan": {
                          "_id": "Free",
                          "createdAt": "1592533498",
                          "modifiedAt": "1592533498",
                          "sms": "0",
                          "email": "30",
                          "notification": "100",
                          "storage": "0.05",
                          "name": "PlanA",
                          "price": "0.00",
                          "bt_plan_id": "Free"
                        },
                        "bt_sub": null
                      },
                      "next": {
                        "_id": null,
                        "plan": {
                          "_id": "Free",
                          "createdAt": "1592533498",
                          "modifiedAt": "1592533498",
                          "sms": "0",
                          "email": "30",
                          "notification": "100",
                          "storage": "0.05",
                          "name": "PlanA",
                          "price": "0.00",
                          "bt_plan_id": "Free"
                        },
                        "bt_sub": null
                      },
                      "draft": null
                    },

    3. Promocode
        A. get user promocodes
        - Request:
        GET: /payment/promocode/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
          "status": "OK",
          "message": "",
          "data": [
            {
              "username": "su-org.1592316898",
              "code": "5eeca30abe5dc00806f53915",
              "expire": "1592186175",
              "info": {
                "_id": null,
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": "10 discount",
                "type": "percent_discount", // real type name not decided yet
                "period": 1,
                "value": "10",  // percentage of discount 
                "remark": "get 10% discount for first month"
              }
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
            'data':{
              "username": "su-org.1592316898",
              "code": "5eeca30abe5dc00806f53915",
              "expire": "1592186175",
              "info": {
                "_id": null,
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": "10 discount",
                "type": "percent_discount", // real type name not decided yet
                "period": 1,
                "value": "10",  // percentage of discount 
                "remark": "get 10% discount for first month"
              }
            },
        }
        
    4. AddOn # TODO

    5. Calculation Prorate
        A. prorate 
        - Request:
        POST: /payment/prorate/calc/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data: { // current PLAN id , and change to PLAN id
            "new_plan_id": 'Enterprise50',
            "old_plan_id": 'Free',
            "promocode": 'the code' // if have
        }
        - Response:
        {
          "status": "OK",
          "message": "",
          "data": {
            "price": "50.00",
            "total_payable": "20.00",
            "plan_rebate": "0.00",
            "total_discount": "0.00",
            "promo_discount": 0.0,
            "prorate": "20.00",
            "remaining_days": 12,
            "total_days": 30,
            "gst": 0.0
          }
        }

    6. payment setup and checkout
        A. get client token   
        - Request:
        GET: /payment/client_token/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            "status": 'OK', 
            "message": '',
            "data": 'the token string',
        }
        
        B. checkout
        - Request:
        POST: /payment/checkout/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:{
              "items": [
                {
                  "subscription_id": "5eec927aa7053179739ac852",
                  "plan_id": "Enterprise50",
                  "promocode": "5eeca30abe5dc00806f53916"
                },
                {...}
              ],
              "nonce": "7fea609c-bad1-07d6-72b0-0a1728cc50ed"
            }
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "data": true
        } 

        C. cancel subscription
        - Request:
        POST: /payment/cancel_subscription/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:{subscription_id: "5eec927aa7053179739ac852"}
        - Response:
        {
            'status': 'OK', 
            'message': string,
            "data": true
        } 

    7. billing address
        A. get billing address  
        - Request:
        GET: /payment/billing_address/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
          "status": "OK",
          "message": "",
          "data": {
            "_id": "5eeb1473e34825134f79c6f7",
            "username": "su-org.1592316898",
            "createdAt": "1592435699",
            "modifiedAt": "1592446926",
            "name": "aaa",
            "billing_address": "bbb",
            "country": "ccc",
            "city": "ddd",
            "postal": "123",
            "region": "aaaaaa"
          }
        }
        
        B. update billing address 
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
          "status": "OK",
          "message": "",
          "data": true
        }

    8. transaction history
        A. GET transactions 
        - Request:
        GET: /payment/transaction/{filter} // e.g. /payment/transaction/?start=2019-01-01&end=2020-01-01
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
          "status": "OK",
          "message": "",
          "data": [
            {
              "_id": "5eeca72bbe5dc00806f53922",
              "username": "su-org.1592316898",
              "createdAt": "1592538786",
              "modifiedAt": "1592538786",
              "start": null,
              "end": null,
              "name": "First Month Payment",
              "value": "20.00",
              "remark": "First Month Payments For Device Plan Subscription",
              "date": "1592538795",
              "status": "pending",
              "bt_trans_id": "0wc3k4rn"
            },
            {...}
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
            "data": {
              "_id": "5eeca72bbe5dc00806f53922",
              "username": "su-org.1592316898",
              "createdAt": "1592538786",
              "modifiedAt": "1592538786",
              "start": null,
              "end": null,
              "name": "First Month Payment",
              "value": "20.00",
              "remark": "First Month Payments For Device Plan Subscription",
              "date": "1592538795",
              "status": "pending",
              "bt_trans_id": "0wc3k4rn"
            },
        }
                 


