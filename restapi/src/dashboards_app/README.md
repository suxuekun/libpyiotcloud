
# SCHEMAS

## Define Charts
```yaml
{
    id: string, # (uuid) 
    name: string,
    userId: string,
    device: {
        id: string,
        type: string #  (Gateways, Sensors, Actuators)
    },
    chartTypeId: string,
    attribute: { # clone from default attribute collection
        id: string , # (uuid)
        systemNamne: string, # (can't modify)
        name: string,
        lables: [],
        filters: [],
    }
}
```

## Define Artribute

```yaml
{
    id: string , # (uuid)
    systemNamne: string,
    name: string,
    lables: [], # id
    filters: [],
}
```

## Define ChartType

```yaml
{
    id: string, #(uuid)
    parrentId: string, # (optional)
    name: string,
    image: string # (optional)
}
```

# GATEWAYS DASHBOAD API  DOCUMENTATION

## Create dashboard requirement:
- As a user can create new gateway dashboards by clicking "Plus Button", and they have to finish follwing these steps:
    1. Select multitple gateways, or select group gateways and click next.
    2. Select/Unselect multitple attributes and click next.
    3. Customize attributes and click next
    4. Select chart and click next
    5. Showing confirmation, user can review information again and click save to go back dashboards screen

* Note After finish to create dashboards, user can see created dashboards. There are some business in here.
    - For Exampe:
        - User select 2 gateways (Gateway1, Gateway2) and select 2 attribute (Count of alert, Online/Offline status), so system will generate 4 Charts with:
            1. Chart of gateway1 has "Count of alert" attribute.
            2. Chart of gateway1 has "Online/ Offline" attribute.
            3. Chart of gateway2 has "Count of alert" attribute.
            4. Chart of gateway2 has "Online/ Offline" attribute.

```yaml

@Endpoint('dashboards/gateways)
@Post()
@Request({
    name: string,
    type: string,
    chartTypeId: string,
    userId: string,
    gateways: [
        {
            id: string,
            groupId: string # (@Optional)
        }
    ],
    atributes: [
        {
            id: string,
            systemName: string,
            name: string,
            lables: [],
            filters: [],
        }
    ]
})
@Response({
    message: "Create dashboards success"
    data: true
})

```

## GET Dashboards gateways
- As a user, I can filter and not filter to get dashboards

* Notes: List dashboard should be grouped by same name's gateway.

```yaml
@Endpoint('dashboards/gateways)
@Get()
@QueryParams({
    attributes: [], # array string,
    gateways: []
})
@Response([
    data: [
        {
            id: string,
            name: string,
            type: string,
            user: {
                id: string,
                name: string,
                groupId: string
            },
            device: {
                id: string,
                groupId: string,
                type: string
            },
            chartType: {
                id: string,
                parrentId: string,
                name: string,
                image: string # optional
            },
            data: {
                dataset: [],
                attribute: {
                    id: string , # (uuid)
                    systemNamne: string, # (can't modify)
                    name: string,
                    lables: [],
                    filters: [],
                },
            }
        }
    ]
])

```

## Update dashboard gateway

- As a user, i can edit dashboards with informations:
    1. Attributes:
        - User just only edit label name or filter type
        - User can't change type of attribute
    2. Chart

```yaml
@Endpoint('dashboards/gateways)
@Put('/{id})
@Request({
    attribute: { # (@Optional)
        lables: [],
        filters: []
    },
    chart: { # (@Optional)
        id: string,
        name: string,
    }
})
```

## Delete dashboad gateway

- As a user, I can delete gateway dashboard

```yaml
@Endpoint('dashboards/gateways)
@Delete('{id}')
@Response({
    data: true,
    message: 'Delete successfully'
})
```

## Get attributes

- As a user, i can get list attribute when creating new gateway dashboads.

```yaml
@Endpoint('dashboards/gateways/attributes)
@Get()
@Response({
    data: [
        {
            id: string , # (uuid)
            systemNamne: string, # (can't modify)
            name: string,
            lables: [],
            filters: [],
        }
    ]
})
```



# SENSORS DASHBOAD API  DOCUMENTATION

## Create sensor dashboard

- As a user can create new sensor dashboard by clicking "Plus button" and they face to finish with these steps:
    1. Select gateway and click next
    2. Select sensor and click next
    3. Select chart and click next
    4. Preview dashboard again and click save

```yaml
@Endpoint('dashboards/sensors')
@Post()
@Request({
    name: string, 
    type: string,
    chartId: string,
    userId: string,
    sensorId: string
})
@Response({
    data: true,
    message: "Create new sensor dashboard successfully"
})
```

## Update sensor dashboard 

- As a user, I can update sensor dashboard with information,
    1. Chart

```yaml
@Endpoint('dashboards/sensors')
@Path('{id}')
@Put()
@Request({
    {
        chartTypeId: string
    }
})
@Response({
    {
        data: true,
        message: 'Update successfully'
    }
})
```

## Get sensors daahboards

- As a user, I can see list group sensor dashboards

* Note: List group dashboard should be grouped by sanme sensor type

```yaml
@Get()
@QueryParams({
    type: string, # sensor type
    gateway: string,
    sensors: [string] # list id
})
@Response({
    data: [
        {
            id: string,
            name: string,
            type: string,
            user: {
                    id: string(uuid),
                    name: string,
                    groupId: string # (@optional)
                },
            device: {
                id: string, #  (gatewaydId/sensorId)
                name: string,
                type: string
            },
            chartType: {
                id: string,
                name: string,
                parentId: string
            },
            data: {
                dataset: [],
                attribute: {
                    id: string , # (uuid)
                    systemNamne: string, # (can't modify)
                    name: string,
                    lables: [],
                    filters: [],
                },
            }
        }
    ]
})
```
## Delete dashboad sensor

- As a user, I can delete gateway dashboard

```yaml
@Endpoint('dashboards/sensors')
@Delete('{dashboardId}')
@Response({
    data: true,
    message: 'Delete successfully'
})
```

## Compare anotther sensor 

- As a user, I can compare existed sensor dashboard to different sensor dashboard by click "Three dots" in item dashobard and select compare. And then, I can select 


```yaml
@Endpoint('dashboards/sensors')
@GET('/compare/{sourceId}/{targetId}')
@Response({
    data: {
        source: {
            device: {
                id: string, #  (gatewaydId/sensorId)
                name: string,
                rootId: string,  # (gatewayId)
                groupId: string # (@optional)
            },
            chartId: string,
            data: {
                dataset: [],
                attribute: {
                    id: string , # (uuid)
                    systemNamne: string, # (can't modify)
                    name: string,
                    lables: [],
                    filters: [],
                },
            }
        },
        target: {
            device: {
                id: string, #  (gatewaydId/sensorId)
                name: string,
                rootId: string,  # (gatewayId)
                groupId: string # (@optional)
            },
            chartId: string,
            data: {
                dataset: [],
                attribute: {
                    id: string , # (uuid)
                    systemNamne: string, # (can't modify)
                    name: string,
                    lables: [],
                    filters: [],
                },
            }
        }
    }
})
```

# Get charts api documentation
- As a user, i can get charts by following type of dashboards

```yaml
@Endpoint('dashboards/charts/types)
@Get()
@QueryParams({
    type: string # Dashboard type (Gateways, Sensors)
})
@Response({
    id: string, #(uuid)
    name: string,
    image: string # (optional)
})
```


