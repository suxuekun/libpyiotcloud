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
        B. UPDATE                          - PUT    /dashboards/{dashboardId}/gateways/{chartId}
        C. GETS                            - GET    /dashboards/{dashboardId}/gateways
        D. GET DETAIL                      - GET    /dashboards/{dashboardId}/gateways/{chartId}
        E. DELETE                          - DELETE /dashboards/{dashboardId}/gateways/{chartId}

    3. Gateway Attritubes:

        A. GETS                            - GET   /dashboards/gateways/attributes

    4. Sensors: 

        A. CREATE                          - POST   /dashboards/{dashboardId}/sensors
        B. UPDATE                          - PUT    /dashboards/{dashboardId}/sensors/{chartId}
        C. GETS                            - GET    /dashboards/{dashboardId}/sensors
        D. GET DETAIL                      - GET    /dashboards/{dashboardId}/sensors/{chartId}
        E. DELETE                          - DELETE /dashboards/{dashboardId}/sensors/{chartId}
        
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
            'options': {
                'color': string
            }
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
            'options': {
                'color': string
            }
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
                    'options': {
                        'color': string
                    }
                }
            ]
        }

        D. GET DETAIL
        - Request:
        GET: /dashboards/{dashboardId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            data: {
                'name': string,
                'id': string,
                'options': {
                    'color': string
                }
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
            'dashboardId': string,
            'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart 
            'gateways': [], # gateways ids
            'attributes': [] # ids
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
        
        B. UPDATE
        - Request:
        PUT: /dashboards/{dashboardId}/gateways/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        data: {
            'attribute': {
                'lables': [],
                'filters': []
            },
            'chartTypeId': string
        }
        - Response:
        {
            'status': 'OK',
            'data': true
            'message': 'Update successfully'
        }
        - Notes:
            Attributes:
            - User just only edit label name or filter type
            - User can't change type of attribute

        C. GETS
        - Request:
        GET: /dashboards/{dashboardId}/gateways
        headers: {'Authorization': 'Bearer ' + token.access}
        queryParams:
            - attributes: [], #ids string
            - gateways: [], #ids string 
        - Response:
        {
            'status': 'OK',
            'data': [
                {
                    'id': string,
                    'device': {
                        'id': string,
                        'name': string,
                    },
                    'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart
                    'dataset': [],
                    'attribute': {
                        'id': string , # (uuid)
                        'name': string,
                        'lables': [],
                        'filters': [],
                    },
                }
            ]
        }

        D. GET
        - Request:
        GET: /dashboards/{dashboardId}/gateways/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        - Response:
        {
            status: 'OK',
            data:  {
                'id': string,
                'device': {
                    'id': string,
                    'name': string,
                },
                'chartTypeId': number, #id # 0: pie, 1: donut description: pie, donut chart
                'dataset': [],
                'attribute': {
                    'id': string , # (uuid)
                    'name': string,
                    'lables': [],
                    'filters': [],
                },
            }
        }

        E. DELETE
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

        B. UPDATE
        - Request:
        PUT: /dashboards/{dashboardId}/sensors/{chartId}
        headers: {'Authorization': 'Bearer ' + token.access}
        data: 
        {
            chartTypeId: number
        }
        - Response:
        {
            'data': true,
            'message': 'Update successfully',
            'status': 'OK' 
        }

        C. GETS
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

        D. GET
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

        E. DELETE
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


SCHEMA DATABASE:

    1. Dashboard:
        {
            id: string,
            name: string,
            userId: string,
            options: {
                color: string
            }
        }

    2. Chart:
        {
            id: string, # (uuid) 
            userId: string,
            dashboardId: string,
            device: {
                id: string,
                type: string #  (Gateways, Sensors, Actuators)
            },
            chartTypeId: string,
            attribute: { # clone from default attribute collection
                id: string , # (uuid)
                name: string,
                lables: [],
                filters: [],
            }
        }
    
    3. Attributes:
        {
            id: string , # (uuid)
            name: string,
            lables: [], # id
            filters: [],
        }

    4. ChartTypes:
        {
            id: number, # 0 : Pie chart
            parrentId: string, # (optional) , reference to root of group chart type
            name: string,
        }

        * Note: In future, one type chart can have multiple child charts type. For example: Pie chart can have pie chart 1, pie chart 2, ...

