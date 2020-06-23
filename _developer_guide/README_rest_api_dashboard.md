 # HTTPS REST API DASHBOARDS Documentation (By Thang)

This is for the front-end (mobile/web) developers.

SUMMARY:

    1. Dashboards:

        A. CREATE                          - POST   /dashboards
        B. UPDATE                          - PUT    /dashboards/{id}
        C. GETS                            - GET    /dashboards
        D. GET DETAIL                      - GET    /dashboards/{id}
        E. DELETE                          - DELETE /dashboards/{id}

    2. Gateways:

        A. CREATE                          - POST   /dashboards/{dashboardId}/gateways
        B. GETS                            - GET    /dashboards/{dashboardId}/gateways
        C. GET DETAIL                      - GET    /dashboards/{dashboardId}/gateways/{chartId}
        D. DELETE                          - DELETE /dashboards/{dashboardId}/gateways/{chartId}

    3. Gateway Attritubes:

        A. GETS                            - GET   /dashboards/gateways/attributes

    4. Sensors: 

        A. CREATE                          - POST   /dashboards/{dashboardId}/sensors
        B. GETS                            - GET    /dashboards/{dashboardId}/sensors
        C. GET DETAIL                      - GET    /dashboards/{dashboardId}/sensors/{chartId}
        D. DELETE                          - DELETE /dashboards/{dashboardId}/sensors/{chartId}
        
    5. ChartTypes:

        A. GETS                            - GET    /dashboards/charts/types/{valueType}


DETAIL:

    1. Dashboards:

        A. CREATE 
        - Request:
        POST: /dashboards
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data: {
            'name': string,
            'color': string
        }
        - Reponse:
        { 
            'status': 'OK', 
            'data': true, 
            'message': 'Create successfully'
        }

        B. UPDATE
        - Request:
        PUT: /dashboards/{id}
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data: {
            'name': string,
            'color': string
        }
        - Reponse:
        { 
            'status': 'OK', 
            'data': true, 
            'message': 'Update successfully'
        }

        C. GETS
        - Request:
        GET: /dashboards
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            data: [
                {
                    'id': string,
                    'name': string,
                    'name': string,
                    'color': string,
                    'createdAt': string
                    'modifiedAt': string
                }
            ]
        }

        D. GET DETAIL
        - Request:
        GET: /dashboards/{dashboardId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            data:{
                    'id': string,
                    'name': string,
                    'name': string,
                    'color': string,
                    'createdAt': string
                    'modifiedAt': string
                }
        }

        E. DELETE
        - Request:
        DELETE: /dashboards/{dashboardId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': true,
            'message': 'Delete successfully'
        }

    2. Gateways

        A. CREATE
        - Request:
        POST: /dashboards/{dashboardId}/gateways/
        headers: {'Authorization': 'Bearer ' + token.access}
        data: {
            'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart 
            'gatewayId': string
            'attributeId': number
        }
        - Response:
        {
            'status': 'OK',
            'data': true,
            'message': 'Create successfully'
        }
        - Note After finish to create charts, there are some business in here.
            - For Exampe:
                - User select 2 gateways (Gateway1, Gateway2) and select 2 attribute (Count of alert, Online/Offline status), so system will generate 4 Charts with:
                    1. Chart of gateway1 has "Count of alert" attribute.
                    2. Chart of gateway1 has "Online/ Offline" attribute.
                    3. Chart of gateway2 has "Count of alert" attribute.
                    4. Chart of gateway2 has "Online/ Offline" attribute.
        
       
        B. GETS
        - Request:
        GET: /dashboards/{dashboardId}/gateways
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - attributeId: string
            - filterId: string, # get from attribute.filters 
        - Response:
        {
            'status': 'OK',
            'data': [
                {
                  "id": string,
                  "typeId": number,
                  "datasets": [
                      {
                          "id": string,
                          "name": string,
                          "value": string,
                      }
                  ],
                  "deviceName": string,
                  "deviceUUID": string,
                  "attribute": {
                      "name: string,
                      "id": string,
                      "filters": [
                          "name": string,
                          "id": number
                      ]
                  }
                }
            ]
        }

        C. GET
        - Request:
        GET: /dashboards/{dashboardId}/gateways/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - attributeId: string
            - filterId: string, # get from attribute.filters 
        - Response:
        {
            status: 'OK',
            data:
                {
                  "id": string,
                  "typeId": number,
                  "datasets": [
                      {
                          "id": string,
                          "name": string,
                          "value": string,
                      }
                  ],
                  "deviceName": string,
                  "deviceUUID": string,
                  "attribute": {
                      "name: string,
                      "id": string,
                      "filters": [
                          "name": string,
                          "id": number
                      ]
                  }
                }
        }

        D. DELETE
        - Request:
        DELETE: /dashboards/{dashboardId}/gateways/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': true
            'message': 'Delete successfully'
        }
    3. Attributes

        A. GETS
        - Request:
        GET: /dashboards/gateways/attributes
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'data': [
                {
                    'id': string ,
                    'name': string
                }
            ]
        }

        B. DATA STRUCTURES
            id: 0 => Storgae Usage
            id: 1 => On-line/Offline status
            id: 2 => Count of alerts
            id: 3 => Upload bandwidth consumption


    4. Sensors

        A. CREATE
        - Request:
        POST: /dashboards/{dashboardId}/sensors
        headers: {'Authorization': 'Bearer ' + token.access}
        data:
        {
            'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart 
            'sensorsId': [] # list sensors id string 
        }
        - Response:
        {
            'data': true,
            'status': 'OK',
            'message': 'Create successfully'
        }

        B. GETS
        - Request:
        GET: /dashboards/{dashboardId}/sensors
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - type: string # sensor type
            - gateway: string
            - sensors: [string] # list id  # note: can use it for merge/compare with different sensors
        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': string,
                    'device': {
                        'id': string, #  (gatewaydId/sensorId)
                        'name': string,
                    },
                    'chartTypeId': string,
                    'dataset': [],
                    'attribute': {
                        'id': string , # (uuid)
                        'systemNamne': string, # (can't modify)
                        'name': string,
                        'lables': [],
                        'filters': [],
                    },
                }
            ]
        }

        C. GET
        - Request:
        GET: /dashboards/{dashboardId}/sensors/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': {
                {
                    'id': string,
                    'device': {
                        'id': string, #  (gatewaydId/sensorId)
                        'name': string,
                    },
                    'chartTypeId': string,
                    'dataset': [],
                    'attribute': {
                        'id': string , # (uuid)
                        'systemNamne': string, # (can't modify)
                        'name': string,
                        'lables': [],
                        'filters': [],
                    },
                }
            }
        }

        D. DELETE
        - Request:
        DELETE: /dashboards/{dashboardId}/sensors/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': true,
            'message': 'Delete successfully'
        }

    5. Charts type
        
        A. GETS
        - Request: 
        GET: /dashboards/charts/types/{valueType}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': number,
                    'name': string,
                }
            ]
        }
        - Notes: 
            {valueType}: gateways, sensors

        B. DATA STRUCTURES

            id: 0 => Pie
            id: 1 => Donut
            id: 2 => Bar
            id: 3 => Line

