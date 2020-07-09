 # HTTPS REST API PAYMENT Documentation (By Su)

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
        B. get user promocode              - GET    /payment/promocode/{code}/
        C. verify                          - POST   /payment/promocode_verify/
        
    4. AddOn # TODO
        A. get addOns                      - GET    /payment/addon/
        B. get addOn Details               - GET    /payment/addon/{id}
        
    5. Calculation Prorate
        A. prorate                         - GET    /payment/prorate/calc/
        
    6. payment setup and checkout
        A. get client token                - GET    /payment/client_token/
        B. checkout                        - POST   /payment/checkout/
        C. cancel subscription             - pOST   /payment/cancel_subscription/
        
    7. billing address
        A. get billing address             - GET    /payment/billing_address/
        B. create billing address          - POST   /payment/billing_address/
        
    8. transaction history
        A. GET transactions                - GET    /payment/transaction/
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
            "message": string,
            "data": [// a list of plan
                {
                    "_id": string,                  // plan id
                    "sms": string,                  // sms limit
                    "email": string,                // email limit
                    "notification": string,         // notification limit 
                    "storage": string,              // storage limit
                    "name": string,                 // plan name
                    "price": string,                // price of plan
                }, 
            ]
        }
        // example
        {
            "status": "OK",
            "message": "",
            "data": [
                {
                    "_id": "Free",
                    "sms": "0",
                    "email": "30",
                    "notification": "100",
                    "storage": "0.05",
                    "name": "Free Plan",
                    "price": "0.00"
                },
                {
                    "_id": "Basic10",
                    "sms": "0",
                    "email": "100",
                    "notification": "1000",
                    "storage": "1",
                    "name": "Basic 10",
                    "price": "10.00"
                },
                {
                    "_id": "Upsize30",
                    "sms": "0",
                    "email": "1000",
                    "notification": "100000",
                    "storage": "3",
                    "name": "Pro 30",
                    "price": "30.00"
                },
                {
                    "_id": "Supersize50",
                    "sms": "0",
                    "email": "10000",
                    "notification": "1000000",
                    "storage": "10",
                    "name": "Enterprise 50",
                    "price": "50.00"
                }
            ]
        }
         
        B. Get Plan Detail
        - Request:
        GET: /payment/plan/{id}/
        headers: {'Content-Type': 'application/json'}
        - Response:
        {
            "status": "OK",
            "message": string,
            "data": {
                "_id": string,                  // plan id
                "sms": string,                  // sms limit
                "email": string,                // email limit
                "notification": string,         // notification limit 
                "storage": string,              // storage limit
                "name": string,                 // plan name
                "price": string,                // price of plan
            }, 
        }
        //example
        {
            "status": "OK",
            "message": "",
            "data": {
                "_id": "Free",
                "sms": "0",
                "email": "30",
                "notification": "100",
                "storage": "0.05",
                "name": "Free Plan",
                "price": "0.00"
            }
        }

    2. Subscription
        A. Get Subscriptions 
        // for cancel_reason:
        // user_internal : user cancel in our IOT Portal
        // uesr_external : user cancel outside our system , e.g. cancel in paypal
        // system        : our system cancel the subscription for reasons e.g. failed to receive recurring payment
        - Request:
        GET: /payment/subscription/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            "status": "OK",
            "message": string,
            "data": [
                {
                    "_id": string,
                    "deviceid": string,
                    "devicename": string,
                    "status": string,                               // 'normal' / 'cancel' / 'downgrade'
                    "cancel_reason": string or null,                // null / 'user_internal' / 'user_external' / 'system'                        
                    "current": {
                        "start": int,                               // start timestamp
                        "end": int,                                 // end timestamp (e.g. end of this month 2020-06-30 23:59:59)
                        "sms": string,                              // current usage of sms
                        "email": string,                            // current usage of email
                        "notification": string,                     // current usage of notificaiton
                        "storage": string,                          // current usage of storage
                        "plan": {                                   
                            "_id": string,                          // plan id
                            "sms": string,                          // sms limit
                            "email": string,                        // email limit
                            "notification": string,                 // notification limit 
                            "storage": string,                      // storage limit
                            "name": string,                         // plan name
                            "price": string,                        // price of plan
                        }
                    },
                    "next": {                                       // next month plan , only if status is 'downgrade', the next month plan is different
                                                                    // 'normal' or 'cancel' status, will be null see example
                        "plan": {
                            "_id": string,                          // plan id
                            "sms": string,                          // sms limit
                            "email": string,                        // email limit
                            "notification": string,                 // notification limit 
                            "storage": string,                      // storage limit
                            "name": string,                         // plan name
                            "price": string,                        // price of plan
                        }
                    }
                },
            ]
        }
        //example 
        {
            "status": "OK",
            "message": string,
            "data": [
                {
                    "_id": "5ef9a5a7653d069466e8d01e",
                    "deviceid": "PH80XXRR0616207E",
                    "devicename": "G1xxxxx",
                    "status": "normal",
                    "cancel_reason": null,
                    "draft_status": false,
                    "current": {
                        "_id": null,
                        "start": 1593390426,
                        "end": 1593532799,
                        "sms": "0",
                        "email": "0",
                        "notification": "0",
                        "storage": "0",
                        "plan": {
                            "_id": "Basic10",
                            "sms": "0",
                            "email": "100",
                            "notification": "1000",
                            "storage": "1",
                            "name": "Basic 10",
                            "price": "10.00"
                        }
                    },
                    "next": null //normal status , so it is same as current
                },
                {
                    "_id": "5ef9a5a7653d069466e8d01f",
                    "deviceid": "PH80XXRR0616208D",
                    "devicename": "G3",
                    "status": "cancel",
                    "cancel_reason": "user_internal",
                    "draft_status": false,
                    "current": {
                        "_id": null,
                        "start": 1593390455,
                        "end": 1593532799,
                        "sms": "0",
                        "email": "0",
                        "notification": "0",
                        "storage": "0",
                        "plan": {
                            "_id": "Upsize30",
                            "sms": "0",
                            "email": "1000",
                            "notification": "100000",
                            "storage": "3",
                            "name": "Pro 30",
                            "price": "30.00"
                        }
                    },
                    "next": null // cancel status so it will be free plan next cycle
                },
                {
                    "_id": "5ef9a623653d069466e8d028",
                    "deviceid": "PH80XXRR062920C2",
                    "devicename": "G5",
                    "status": "downgrade",
                    "cancel_reason": null,
                    "draft_status": false,
                    "current": {
                        "_id": null,
                        "start": 1593390542,
                        "end": 1593532799,
                        "sms": "0",
                        "email": "0",
                        "notification": "0",
                        "storage": "0",
                        "plan": {
                            "_id": "Supersize50",
                            "sms": "0",
                            "email": "10000",
                            "notification": "1000000",
                            "storage": "10",
                            "name": "Enterprise 50",
                            "price": "50.00"
                        }
                        
                    },
                    "next": {   // current month is Supersize50 but will downgrade to Upsize30 next month
                        "plan": {
                            "_id": "Upsize30",
                            "sms": "0",
                            "email": "1000",
                            "notification": "100000",
                            "storage": "3",
                            "name": "Pro 30",
                            "price": "30.00"
                        }
                    }
                },
                {
                    "_id": "5ef9a623653d069466e8d029",
                    "deviceid": "PH80XXRR06292020",
                    "devicename": "G7",
                    "status": "normal",
                    "cancel_reason": null,
                    "draft_status": false,
                    "current": {
                        "_id": null,
                        "start": 1593390499,
                        "end": 1593532799,
                        "sms": "0",
                        "email": "0",
                        "notification": "0",
                        "storage": "0",
                        "plan": {
                            "_id": "Free",
                            "sms": "0",
                            "email": "30",
                            "notification": "100",
                            "storage": "0.05",
                            "name": "Free Plan",
                            "price": "0.00"
                        }
                    },
                    "next": null
                }
            ]
        }
        
        B. Get Subscription Detail
        - Request:
        GET: /payment/subscription/{id}/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            "status": "OK",
            "message": "",
            "data": {
                    "_id": string,
                    "deviceid": string,
                    "devicename": string,
                    "status": string,                               // 'normal' / 'cancel' / 'downgrade'
                    "cancel_reason": string or null,                // null / 'user_internal' / 'user_external' / 'system'                        
                    "current": {
                        "start": int,                               // start timestamp
                        "end": int,                                 // end timestamp (e.g. end of this month 2020-06-30 23:59:59)
                        "sms": string,                              // current usage of sms
                        "email": string,                            // current usage of email
                        "notification": string,                     // current usage of notificaiton
                        "storage": string,                          // current usage of storage
                        "plan": {                                   
                            "_id": string,                          // plan id
                            "sms": string,                          // sms limit
                            "email": string,                        // email limit
                            "notification": string,                 // notification limit 
                            "storage": string,                      // storage limit
                            "name": string,                         // plan name
                            "price": string,                        // price of plan
                        }
                    },
                    "next": {                                       // next month plan , only if status is 'downgrade', the next month plan is different
                                                                    // 'normal' or 'cancel' status, will be null see example
                        "plan": {
                            "_id": string,                          // plan id
                            "sms": string,                          // sms limit
                            "email": string,                        // email limit
                            "notification": string,                 // notification limit 
                            "storage": string,                      // storage limit
                            "name": string,                         // plan name
                            "price": string,                        // price of plan
                        }
                    }
                },
        }
        //example
        {
            "status": "OK",
            "message": "",
            "data": {
                "_id": "5ef9a5a7653d069466e8d01e",
                "deviceid": "PH80XXRR0616207E",
                "devicename": "G1xxxxx",
                "status": "normal",
                "cancel_reason": null,
                "current": {
                    "_id": null,
                    "start": 1593390426,
                    "end": 1593532799,
                    "sms": "0",
                    "email": "0",
                    "notification": "0",
                    "storage": "0",
                    "plan": {
                        "_id": "Basic10",
                        "sms": "0",
                        "email": "100",
                        "notification": "1000",
                        "storage": "1",
                        "name": "Basic 10",
                        "price": "10.00"
                    }
                },
                "next": null
            }
        }

    3. Promocode

        // types of promocode: 
        // 'discount'       : $ discount
        // 'p_discount'     : percentage discount
        //
        // promocode value attribute depends on type , the value is usually a decimal string,(later may have other format values)
        // e.g. 
        // if type is discount,  value = '5.00' means $5.00 discount
        // if type is p_discount,value = '5.0' means 5% discount
        //
        // currently no other types , sms and other addons are NOT depend on type( in alpha 2 )
        //

        A. get user promocodes
        // get user promocode avaliable for which subscription update to which plan 

        - Request:
        GET: /payment/promocode/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        queryParams:
          subscription_id: string,  // the subscription_id which will use this promocode 
          plan_id: string,          // the plan id which subscription will change to 
        - Response:
        {
          "status": "OK",
          "message": string,
          "data": [
            {
                "_id": string,                        // _id is also promocode
                "start": int,                         // start timestamp
                "end": int,                           // end timestamp
                "name": string,
                "type": string,                       // 'discount' / 'p_discount' / '' 
                "value": string,                      // a decimal string , if percentage , '5' = 5%
                "sms": string,                        // sms addon
                "email": string,                      // email addon
                "notification": string,               // notification addon
                "storage": string,                    // storage addon
                "remark": string,                     // description text
                "period": int,                        // promocode effect last for {period} month
                "plans": [string],                    // a list of string which plan can use this promocode
                "max_usage": int                      // this promocode can be used for how many times for a device (not for a user)
            }
          ]
        }

        //example
        {
          "status": "OK",
          "message": "",
          "data": [
            {
              "_id": "D05-30-50-twice",
              "start": 1593532800,
              "end": 1594742400,
              "name": "$5.00 ",
              "type": "discount",
              "value": "5",
              "sms": "0",
              "email": "0",
              "notification": "0",
              "storage": "0",
              "remark": "$5 discount",
              "period": 1,
              "plans": [
                "Upsize30",
                "Supersize50"
              ],
              "max_usage": 2
            },
            {
              "_id": "PD10-30-50-twice",
              "start": 1594742400,
              "end": 1596124800,
              "name": "10%",
              "type": "p_discount",
              "value": "10.0",
              "sms": "0",
              "email": "0",
              "notification": "0",
              "storage": "0",
              "remark": "get 10% discount for current month",
              "period": 1,
              "plans": [
                "Upsize30",
                "Supersize50"
              ],
              "max_usage": 2
            }
          ]
        }
        // missing params 
        {
            "status": "NG",
            "message": "Bad Request"
        }
        // wrong subscription_id or plan_id will always return empty list but with ok status
        {
            "status": "OK",
            "message": "",
            "data": []
        }
        
        B. get user promocodes
        - Request:
        GET: /payment/promocode/{code}/
        // if code exist then return this code , no checking on plan and validity period
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            "status": "OK",
            "message": string,
            "data": {
                "_id": string,                        // _id is also promocode
                "start": int,                         //start timestamp
                "end": int,                           //end timestamp
                "name": string,
                "type": string,                       // 'discount' / 'p_discount' / '' 
                "value": string,                      // a decimal string , if percentage , '5.0' = 5%
                "sms": string,                        // sms addon
                "email": string,                      // email addon
                "notification": string,               // notification addon
                "storage": string,                    // storage addon
                "remark": string,                     // description text
                "period": int,                        // promocode effect last for {period} month
                "plans": [string],                    // a list of string which plan can use this promocode
                "max_usage": int                      // this promocode can be used for how many times for a device (not for a user)
            }
        }
        //example
        {
            "status": "OK",
            "message": "",
            "data": {
                "_id": "D05-30-50-twice",
                "start": 1593532800,
                "end": 1594742400,
                "name": "$5.00 discount",
                "type": "discount",
                "value": "5",
                "sms": "0",
                "email": "0",
                "notification": "0",
                "storage": "0",
                "remark": "$5 discount for user, each device can use twice",
                "period": 1,
                "plans": [
                  "Upsize30",
                  "Supersize50"
                ],
                "max_usage": 2
              }
        }
        // NG
        {
            "status": "NG",
            "message": "Data Not Found"
        }

        C. verify promocode 
        - Request:
        POST : /payment/promocode_verify/
        // verify if the code is avaliable for subscription change to the specific plan
         
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
          subscription_id: string,  // the subscription_id which will use this promocode 
          plan_id: string,          // the plan id which subscription will change to 
          code: string,             // promocode id ( the id is also the code)
        - Response:
        {
            "status": "OK",
            "message": string,
            "data": {
                "_id": string,
                "start": int,                         //start timestamp
                "end": int,                           //end timestamp
                "name": string,
                "type": string,                       // 'discount' / 'p_discount' / '' 
                "value": string,                      // a decimal string , if percentage , '5.0' = 5%
                "sms": string,                        // sms addon
                "email": string,                      // email addon
                "notification": string,               // notification addon
                "storage": string,                    // storage addon
                "remark": string,                     // description text
                "period": int,                        // promocode effect last for {period} month
                "plans": [string],                    // a list of string which plan can use this promocode
                "max_usage": int                      // this promocode can be used for how many times for a device (not for a user)
            }
        }
        //example
        {
            "status": "OK",
            "message": "",
            "data": {
                "_id": "D05-30-50-twice",
                "start": 1593532800,
                "end": 1594742400,
                "name": "$5.00 discount",
                "type": "discount",
                "value": "5",
                "sms": "0",
                "email": "0",
                "notification": "0",
                "storage": "0",
                "remark": "$5 discount for user, each device can use twice",
                "period": 1,
                "plans": [
                  "Upsize30",
                  "Supersize50"
                ],
                "max_usage": 2
            }
        }
        // NG 
        {
            "status": "NG",
            "message": "NO CODE FOUND OR CODE NOT AVALIABLE FOR THIS PLAN"
        }
        
    4. AddOn # TODO

    5. Calculation Prorate
        //
        //prorate formula
        //
        // basic attributes
        // 0 old_plan_price             -- if have old plan( upgrade scenario ), the old plan's price
        // 1 price                      -- the updated plan price
        // 2 remaining_days             -- days left in this month
        // 3 total_days                 -- total days in this month
        // 4 gst                        -- gst percentage ("7.00" = 7%)
        // 5 promo_value.               -- have 2 types curretly( percentage_discount/ discount)
        
        // calculated
        //
        // 1 total_payable                      -- total_payable = price * (remaing_days/total_days)
        // 2 plan_rebate                        -- plan_rebate = old_plan_price * (remain_days/total_days)
        // 3 promo_discount               
                -- if percentage_discount          promo_discount = (total_payable - plan_rebate) * promo_value
                -- if discount.                    promo_discount = promo_value.    ( but can not bigger than total_payable - plan_rebate)

        // 4 total_discount                     -- total_discount = plan_rebate + promo_discount
        // 5 prorate                            -- total_payable - total_discount
        // 
        // for gst 
        //
        // 6 gst_amount                         -- gst_amount = prorate * gst/100
        // 7 gst_price                          -- gst_price = price * ( 1 + gst/100 )
        // 8 gst_prorate                        -- gst_prorate = prorate * ( 1 + gst/100 )
        //
        //
        // e.g.  for case $30 plan update to $50 plan on 15th of month (15/30) for Singapore customer
        //
        // old_plan_price           = 30.00
        // price                    = 50.00
        // remaining_days           = 15.00
        // total_days               = 30.00
        // gst                      = 7   (7% gst)
        // promo_value              = 20  (20% discount)
        //
        // total_payable            = 50 * ( 15/30)             = 25.00
        // plan_rebate              = 30 * ( 15/30)             = 15.00
        // promo_discount           = ( 25 - 15 ) * 20%=10*20%  = 2.00
        // total_discount           = 15.00 + 2.00              = 17.00
        // prorate                  = 25.00 - 17.00             = 8.00   (final payment before gst)
        // gst_amount               = 8.00 * 7%                 = 0.56
        // gst_price                = 50 * (1+7%)               = 53.50  ( the price show to customer including gst)
        // gst_prorate              = 8.00 * (1+7%)             = 8.56   (final payment including gst) 


        A. prorate 
        - Request:
        GET: /payment/prorate/calc/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        queryParams:
            "new_plan_id": string,                //example: 'Supersize50',
            "old_plan_id": string,                //example: 'Basic10',
            "promocode": string                   //example: 'the code' // if have
        
        - Response:
        {
          "status": "OK",
          "message": string,
          "data": {
            "price": string,                      // price of the new plan
            "total_payable": string,              // prorated price of the new plan
            "plan_rebate": string,                // old plan rebate
            "total_discount": string,             // all discount add together  total_discount = plan_rebate + promo_discount
            "promo_discount": string,             // discount from promocode
            "prorate": string,                    // the prorated amount to PAY
            "remaining_days": int,                // remaining days of this month
            "total_days": int,                    // total days of this month
            "gst": string,                        // gst "7.00" = 7% if avaliable
            "gst_amount": string,                 // gst amount = prorate * gst/100 ( the gst amount in USD)
            "gst_price": string,                  // if have gst then have the gst_price = (1+gst/100) * price             
            "gst_prorate": string                 // if have gst then have the gst_prorate = (1+gst/100) * prorate
          }
        }
        //example
        {
            "status": "OK",
            "message": "",
            "data": {
                "price": "50.00",                 //  Supersize50 price is 50
                "total_payable": "3.33",          //  50 * 2/30 = 3.33
                "plan_rebate": "0.67",            //  basic plan price is 10 , 10 * 2/30 = 0.67 need to rebate 
                "total_discount": "3.33",         //  0.67 + 2.66 = 3.33
                "promo_discount": "2.66",         //  promocode have $5 discount , but total payment less than $5 so only 2.66
                "prorate": "0.00",                //  payment is 0.00 
                "remaining_days": 2,              //  2 days left in this month
                "total_days": 30,                 //  30 days total in this month
                "gst": "7.00"                     //  if have gst
                "gst_price": "53.50"              //  then have gst_price
                "gst_prorate": "1.7869"           //  and also have gst_proraed
            }
        }
        {
            "status": "OK",
            "message": "",
            "data": {
                "price": "50.00",                 //  Supersize50 price is 50
                "total_payable": "3.33",          //  50 * 2/30 = 3.33
                "plan_rebate": "0.67",            //  basic plan price is 10 , 10 * 2/30 = 0.67 need to rebate 
                "total_discount": "3.33",         //  0.67 + 2.66 = 3.33
                "promo_discount": "2.66",         //  promocode have $5 discount , but total payment less than $5 so only 2.66
                "prorate": "0.00",                //  payment is 0.00 
                "remaining_days": 2,              //  2 days left in this month
                "total_days": 30,                 //  30 days total in this month
                "gst": "0.00"                     //  no gst
            }
        }
        // with invalid promocode will return normally but with bad promocode message
        {
            "status": "OK",
            "message": "bad promocode",
            "data": {
                "price": "50.00",
                "total_payable": "3.33",
                "plan_rebate": "0.00",
                "total_discount": "0.00",
                "promo_discount": "0.00",
                "prorate": "3.33",
                "remaining_days": 2,
                "total_days": 30,
                "gst": "0.00"
            }
        }
        // with invalid new_plan_id or old_plan_id
        {
            "status": "NG",
            "message": "bad new plan id"
        }
        {
            "status": "NG",
            "message": "bad old plan id"
        }
        // missing new_plan_id or old_plan_id
        {
            "status": "NG",
            "message": "Bad Request"
        }

    6. payment setup and checkout
        A. get client token   
        // client_token is a token frontend get from backend, (which backend get from braintree with customer_id)
        // client_token is for geting a one time use nonce for frontend from braintree 
        // nonce is a string , only can be used for one time
        // front end need to pass the nonce to backend when checkout
        // backend will provide the nonce to braintree to get the payment token for user transaction or subscription changes
        

        - Request:
        GET: /payment/client_token/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            "status": 'OK', 
            "message": string,
            "data": {
                "token":string // the token string
            },           
        }
        
        B. checkout
        - Request:
        POST: /payment/checkout/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:
        {
              "items": [ // can have many changes in one run in this api
                {
                  "subscription_id": string,            // the subscription id which will change
                  "plan_id": string,                    // the plan which changing to 
                  "promocode": string,                  // promocode applied on this change
                },
              ],
              "nonce": string, // the nonce get from braintree 
            }

        //example
        {
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
        } 
        // wrong post data format http : 400
        {
            "status": "NG",
            "message": "Bad Request"
        }
        // problem with braintree httpcode : 503
        {'status': 'NG', 'message': 'check out fail with braintree'}
        // problem with data base format  httpcode: 503
        {'status':'NG','message':'data format fail'}

        C. cancel subscription
        - Request:
        POST: /payment/cancel_subscription/
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data:{subscription_id: "5eec927aa7053179739ac852"}
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
          "status": "OK",
          "message": string,
          "data": {
            "name": string,
            "billing_address": string,
            "country": string,
            "city": string,
            "postal": string,
            "region": string
          }
        }
        //example
        {
          "status": "OK",
          "message": "",
          "data": {
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
            name: string,
            billing_address:string,
            country:string,
            city:string,
            postal:string,
            region:string,
        }
        //example
        {
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
          "message": string,
        }
        {
          "status": "NG",
          "message": string,
        }

    8. transaction history
        A. GET transactions 
        - Request:
        GET: /payment/transaction/{filter} // e.g. /payment/transaction/?start=2019-01-01&end=2020-01-01
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        - Response:
        {
            "status": "OK",
            "message": string,
            "data": [
                {
                    "_id": string,
                    "start": int,               // start timestamp if it is a record of recurring payment
                    "end": int,                 // end timestamp if it is a record of recurring payment
                    "name": string,             
                    "value": string,            // payment amount
                    "remark": string,           // description
                    "date": int,                // payment date timestamp
                    "status": string,           // payment status    // not defined yet, will align to braintree transaction status
                    "receipt": string,          // receipt pdf url   // not impl yet
                    "bt_trans_id": string       // the transaction id from braintree 
                }
            ]
        }
        //example
        {
            "status": "OK",
            "message": "",
            "data": [
                {
                    "_id": "5eeca72bbe5dc00806f53922",
                    "start": null,
                    "end": null,
                    "name": "First Month Payment",
                    "value": "20.00",
                    "remark": "First Month Payments For Device Plan Subscription",
                    "date": 1592538795,
                    "status": "pending",
                    "receipt": null,
                    "bt_trans_id": "0wc3k4rn"
                },
                {
                    "_id": "5ef6edeeae465919081d4358",
                    "start": null,
                    "end": null,
                    "name": "First Month Payment",
                    "value": "6.003",
                    "remark": "First Month Payments For Device Plan Subscription",
                    "date": 1593212270,
                    "status": "pending",
                    "receipt": null,
                    "bt_trans_id": "5znqtyav"
                }
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
                "_id": string,
                "start": int,               // start timestamp if it is a record of recurring payment
                "end": int,                 // end timestamp if it is a record of recurring payment
                "name": string,             
                "value": string,            // payment amount
                "remark": string,           // description
                "date": int,                // payment date timestamp
                "status": string,           // payment status    // not defined yet, will align to braintree transaction status
                "receipt": string,          // receipt pdf url   // not impl yet
                "bt_trans_id": string       // the transaction id from braintree 
            }
        }
        
                 


