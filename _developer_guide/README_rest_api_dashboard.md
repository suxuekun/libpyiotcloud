 # HTTPS REST API DASHBOARDS Documentation (By Thang)

This is for the front-end (mobile/web) developers.

SUMMARY:

    1. Dashboards:

        A. CREATE                          - POST   /dashboards
        B. UPDATE                          - PUT    /dashboards/dashboard/{dashboardId}
        C. GETS                            - GET    /dashboards
        D. GET DETAIL                      - GET    /dashboards/dashboard/{dashboardId}
        E. DELETE                          - DELETE /dashboards/dashboard/{dashboardId}

    2. Gateways:

        A. CREATE                          - POST   /dashboards/dashboard/{dashboardId}/gateways
        B. GETS                            - GET    /dashboards/dashboard/{dashboardId}/gateways
        C. GET DETAIL                      - GET    /dashboards/dashboard/{dashboardId}/gateways/{chartId}
        D. DELETE                          - DELETE /dashboards/dashboard/{dashboardId}/gateways/{chartId}
        
    3. Gateway Attritubes:

        A. GETS                            - GET   /dashboards/gateway/attributes

    4. Sensors: 

        A. CREATE                          - POST   /dashboards/dashboard/{dashboardId}/sensors
        B. GETS                            - GET    /dashboards/dashboard/{dashboardId}/sensors
        C. GET DETAIL                      - GET    /dashboards/dashboard/{dashboardId}/sensors/{chartId}
        D. DELETE                          - DELETE /dashboards/dashboard/{dashboardId}/sensors/{chartId}
        E. COMPARE                         - GER    /dashboards/dashboard/{dashboardId}/sensors/comparison

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
            'message': 'Create successfully'
        }

        B. UPDATE
        - Request:
        PUT: /dashboards/dashboard/{dashboardId}
        headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        data: {
            'name': string,
            'color': string
        }
        - Reponse:
        { 
            'status': 'OK', 
            'message': 'Update successfully'
        }

        C. GETS
        - Request:
        GET: /dashboards
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': string,
                    'name': string,
                    'color': string,
                    'createdAt': string
                    'modifiedAt': string
                }
            ],
            'message': 'Get dashboards successfully'
        }

        D. GET DETAIL
        - Request:
        GET: /dashboards/dashboard/{dashboardId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK'
            'data':{
                    'id': string,
                    'name': string,
                    'color': string,
                    'createdAt': string
                    'modifiedAt': string
            },
            'message': 'Get dashboard detail successfully'
        }

        E. DELETE
        - Request:
        DELETE: /dashboards/dashboard/{dashboardId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'message': 'Delete successfully'
        }

    2. Gateways

        A. CREATE
        - Request:
        POST: /dashboards/dashboard/{dashboardId}/gateways
        headers: {'Authorization': 'Bearer ' + token.access}
        data: {
            'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart 
            'deviceId': string
            'attributeId': number
        }
        - Response:
        {
            'status': 'OK',
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
        GETS: /dashboards/dashboard/{dashboardId}/gateways
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams: 
            - mobile: true or false (default=false, optional)
        - Response:
        {
            'status': 'OK',
            'message, 'Get chart responses successfully',
            'data': [
                {
                  "id": string,
                  "chartTypeId": number,
                  "datasets": [
                      {
                        "filterId": number,
                        "filterName": string,
                        "labels": [string],
                        "data": [number],
                      }
                  ],
                  "datasetsEx": [  (* if 'mobile' is true)
                      {
                          "filterId": number,
                          "filterName": string,
                          "values": [
                            {
                                "label": string,
                                "data": number,
                            }
                          ]
                      }
                  ],
                  "device": {
                      "name": string,
                      "uuid": string
                  },
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

        C. GET_DETAIL
        - Request:
        GETS: /dashboards/dashboard/{dashboardId}/gateways/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams: 
            - mobile: true or false (default=false, optional)
        - Response:
        {
            'status': 'OK',
            'message, 'Get chart responses successfully',
            'data': {
                  "id": string,
                  "chartTypeId": number,
                  "datasets": [
                      {
                        "filterId": number,
                        "filterName": string,
                        "labels": [string],
                        "data": [number],
                      }
                  ],
                  "datasetsEx": [ (* if 'mobile' is true)
                      {
                          "filterId": number,
                          "filterName": string,
                          "values": [
                            {
                                "label": string,
                                "data": number,
                            }
                          ]
                      }
                  ],
                  "device": {
                      "name": string,
                      "uuid": string
                  },
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
        DELETE: /dashboards/dashboard/{dashboardId}/gateways/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'message': 'Delete successfully'
        }

    3. Attributes

        A. GETS
        - Request:
        GET: /dashboards/gateway/attributes
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': string ,
                    'name': string
                }
            ],
            'message': 'Get attributes successully'
        }

        B. DATA STRUCTURES
            id: 0 => Storgae Usage
            id: 1 => On-line/Offline status
            id: 2 => Count of alerts
            id: 3 => Upload bandwidth consumption

    4. Sensors

        A. CREATE
        - Request:
        POST: /dashboards/dashboard/{dashboardId}/sensors
        headers: {'Authorization': 'Bearer ' + token.access}
        data:
        {
            'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart 
            'source': string,  # get from api sensors
            'number': string   # get from api sensors
        }
        - Response:
        {
            'status': 'OK',
            'message': 'Create successfully'
        }

        B. GETS
        - Request:
        GET: /dashboards/dashboard/{dashboardId}/sensors
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - minutes: int (optional, default = 5, descriptions: value should in 5, 15, 30, 60, 1440, 10080)
            - timestamp: int (optional)
            - points: int  (optional, descriptions: value should in 30 or 60)
            - mobile: true or false (default=false, optional)    
            - selected_minutes: string  (optional)
            - chartsId: string  (optional)

            * Note:
            - minutes: int  (default = 5 min, should convert hour or day to minutes)
            - timestamp: int (default = currentTime now, unit of timestamp is unix timestamp. For example: 1593760508 )
            - selected_minutes: string (example: &selected_minutues=15,30) 
            - chartsId: string (example: &chartsId=5f04962217e8e565d1fd4adf,5f04966117e8e565d1fd4ae2 )  

        selected_minutes & chartsId shoulb be the same size and match index together
        For Example: &selected_minutes=15,30&chartsId=5f04962217e8e565d1fd4adf,5f04966117e8e565d1fd4ae2
            - chartId: 5f04962217e8e565d1fd4adf select time range is 15 minutes
            - chartId: 5f04966117e8e565d1fd4ae2 select time range is 30 minutes

        If we have 3 charts but we send request with "&selected_minutes=15,30&chartsId=5f04962217e8e565d1fd4adf,5f04966117e8e565d1fd4ae2". 
        The another chart without selected timeRange will be use value default is 15

        Example request: /dashboards/dashboard/5ef998655de8966f2de5064e/sensors?minutes=5&points=30

        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': string,
                    'chartTypeId': int,
                    'selectedMinutes': int,
                    'device': {
                        'id': string, #  (gatewaydId/sensorId)
                        'name': string,
                        'source': string,
                        'port': int,
                        'name': string,
                        'sensorClass': string,
                        'gatewayUUID': string,
                        'gatewayName': string,
                        'minmax': [
                            string
                        ],
                        'accuracy': float,
                        'unit': string,
                        'format': string,
                        'enabled': int,
                    },
                    'datasets': [
                        {
                            'data': [float],
                            'lables': [int],
                            'low': [float],
                            'high': [float]
                        }
                    ],
                    'datasetsEx': [ (#if mobile is false)
                        {
                           'x': int,
                           'y': float,
                           'high': float,
                           'low': float
                        }
                    ],
                    'readings: [
                        {
                            highest: float,
                            lowest: float,
                            value float
                        }
                    ]
                }
            ],
            'message': 'Get charts sensors successfully'
        }

        C. GET
        - Request:
        GET: /dashboards/dashboard/{dashboardId}/sensors/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - minutes: int (optional, default = 5, descriptions: value should in 5, 15, 30, 60, 1440, 10080)
            - timestamp: int (optional)
            - points: int  (optional, descriptions: value should in 30 or 60)
            - mobile: true or false (default=false, optional)
       
            * Note:
            - minutes: int  (default = 5 min, should convert hour or day to minutes)
            - timestamp: int (default = currentTime now, unit of timestamp is unix timestamp. For example: 1593760508 )

        Example request: /dashboards/dashboard/5ef998655de8966f2de5064e/sensors/5efc2c38cc25092a0c952291?minutes=5&points=30
        

        - Response:
        {
            'status': 'OK',
            'data': {
                {
                    'id': string,
                    'chartTypeId': int,
                    'selectedMinutes': int,
                    'device': {
                        'id': string, #  (gatewaydId/sensorId)
                        'name': string,
                        'source': string,
                        'port': int,
                        'name': string,
                        'sensorClass': string,
                        'gatewayUUID': string,
                        'gatewayName': string,
                        'minmax': [
                            string
                        ],
                        'accuracy': float,
                        'unit': string,
                        'format': string,
                        'enabled': int
                    },
                    'datasets': [
                        {
                            'data': [float],
                            'lables': [int],
                            'low': [float],
                            'high': [float]
                        }
                    ],
                    'datasetsEx': [ (#if mobile is false)
                        {
                           'x': int,
                           'y': float,
                           'high': float,
                           'low': float
                        }
                    ],
                    'readings: [
                        {
                            highest: float,
                            lowest: float,
                            value float
                        }
                    ]
                }
            },
            'message': 'Get chart detail successfully'
        }
        

        D. DELETE
        - Request:
        DELETE: /dashboards/dashboard/{dashboardId}/sensors/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            'status': 'OK',
            'message': 'Delete successfully'
        }

        E. COMPARE

        - Request:
        GET: /dashboards/dashboard/{dashboardId}/sensors/comparison
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - minutes: int  (optional,)
            - timestamp: int (optional)
            - points: int  (optional)
            - chartsId: string (require, max = 3, min = 2)
            - mobile: true or false (default=false, optional)

            * Note:
            - minutes: int  (default = 5 min, should convert hour or day to minutes)
            - timestamp: int (default = currentTime now, unit of timestamp is unix timestamp. For example: 1593760508 )
            - chartsId: string (example: &chartsId=5f04962217e8e565d1fd4adf,5f04966117e8e565d1fd4ae2 )
            
        Example request:
        /dashboards/dashboard/5ef998655de8966f2de5064e/sensors/comparison?chartsId=5efc2c38cc25092a0c952291,5efc3128c6c8bd539d036f28

        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': string,
                    'chartTypeId': int,
                    'selectedMinutes': int,
                    'device': {
                        'id': string, #  (gatewaydId/sensorId)
                        'name': string,
                        'source': string,
                        'port': int,
                        'name': string,
                        'sensorClass': string,
                        'gatewayUUID': string,
                        'gatewayName': string,
                        'minmax': [
                            string
                        ],
                        'accuracy': float,
                        'unit': string,
                        'format': string,
                        'enabled': int
                    },
                    'datasets': [
                        {
                            'data': [float],
                            'lables': [int],
                            'low': [float],
                            'high': [float]
                        }
                    ],
                    'datasetsEx': [ (#if mobile is false)
                        {
                           'x': int,
                           'y': float,
                           'high': float,
                           'low': float
                        }
                    ],
                    'readings: [
                        {
                            highest: float,
                            lowest: float,
                            value float
                        }
                    ]
                }
            ],
            'message': 'Get charts sensors successfully'
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
            'message': 'Get chart responses successfully'
        }
        - Notes: 
            {valueType}: gateway, sensor

        B. DATA STRUCTURES

            id: 0 => Pie
            id: 1 => Donut
            id: 2 => Bar
            id: 3 => Line

