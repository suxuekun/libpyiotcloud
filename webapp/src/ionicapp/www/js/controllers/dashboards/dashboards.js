let timerChartSensor = {};

angular.module('app.dashboardsCtrl', [])
  .controller('dashboardsCtrl', ['$scope', '$stateParams', '$state', '$filter', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $state, $filter, $ionicPopup, $http, Server, User, DateTimeUtil) {

      $scope.data = {
        'search': '',
        'token': User.get_token(),
      };
      const defaultColor = "#f2495e";
      $scope.dashboardDetail = {};
      $scope.selectedColor = defaultColor;

      const server = Server.rest_api;
      let cachedDashboards = [];

      // Start the page
      $scope.$on('$ionicView.enter', (e) => {
        $scope.data.token = User.get_token();
        $scope.getDashboards();
      });

      $scope.$on("$ionicView.beforeLeave", function () {
        console.log("Clear timer");
        clearInterval(timerChartSensor);
      });

      // Init life cycle
      $scope.add = () => {
        const device_param = {}
        $state.go('addDashboard', device_param, {
          reload: true
        });
      }

      //  Scope of list dashboards
      $scope.submitSearch = () => {
        const searchKey = $scope.data.search;
        console.log(searchKey)
        if (!searchKey) {
          renderDashdoards(cachedDashboards)
          return;
        }
        const foundDashboards = cachedDashboards.filter((d) => d.name.includes(searchKey));
        renderDashdoards(foundDashboards);
      }

      $scope.delete = (id) => {
        $ionicPopup.alert({
          title: 'Remove dashboard',
          template: 'Are you sure to remove it ?',
          buttons: [{
              text: 'Yes',
              type: 'button-positive',
              onTap: (e) => {
                $http({
                    method: 'DELETE',
                    url: `${server}/dashboards/dashboard/${id}`,
                    headers: {
                      'Authorization': 'Bearer ' + $scope.data.token.access,
                      'Content-Type': 'application/json'
                    }
                  })
                  .then(function (result) {
                    console.log(result.data);
                    const dashboards = $scope.dashboards
                    cachedDashboards.splice(cachedDashboards.findIndex((d) => d.id === id), 1)
                    $scope.dashboards.splice($scope.dashboards.findIndex((d) => d.id === id), 1);
                    if ($scope.dashboards.length > 0)
                      $scope.viewDetail($scope.dashboards[0])
                  })
                  .catch(function (error) {
                    console.error(error);
                    $ionicPopup.alert({
                      title: 'Dashboard',
                      template: 'Delete dashboard failed!',
                    });
                  });
              }
            },
            {
              text: 'No',
              type: 'button-positive',
              onTap: (e) => true
            }
          ]
        });
      }

      $scope.viewDetail = (dashboard) => {
        $scope.dashboardDetail = dashboard;
        $scope.selectedColor = $scope.dashboardDetail.color ? `${$scope.dashboardDetail.color}` : defaultColor;
        switch($scope.activeTab) {
          case 0:
            getChartGateways();
            return;
          case 1:
            getChartSensors();
            return;
        }

      }

      // Init private functions
      renderDashdoards = (dashboards) => {
        $scope.dashboards = dashboards.map((d) => {
          return {
            id: d.id,
            color: `#${d.color}`,
            name: d.name,
            createdAt: $filter('date')(DateTimeUtil.convertTimestampToDate(d.createdAt), "dd/MM/yyyy hh:mm"),
            modifiedAt: $filter('date')(DateTimeUtil.convertTimestampToDate(d.modifiedAt), "dd/MM/yyyy hh:mm")
          }
        });
      }

      $scope.getDashboards = () => {
        $http({
            method: 'GET',
            url: server + '/dashboards',
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            cachedDashboards = result.data.data;
            renderDashdoards(cachedDashboards);
            if (cachedDashboards.length > 0) {
              $scope.dashboardDetail = cachedDashboards[0];
              $scope.selectedColor = $scope.dashboardDetail.color ? `#${$scope.dashboardDetail.color}` : defaultColor;
              getChartGateways();
            }
          })
          .catch(function (error) {
            console.log(error);
          });
      }
      // Scope of dashboard detail
      $scope.sensors_datachart_colors_options = ['#11C1F3', '#33CD5F', '#FFC900', '#F38124', '#EF473A', '#F58CF6', '#B6A2FC', '#3C5A99'];
      $scope.sensors_datachart_colors_options_ex = ['#EF473A', '#F38124', '#FFC900', '#33CD5F', '#11C1F3', '#3C5A99', '#B6A2FC', '#F58CF6'];
      $scope.sensors_datachart_colors_options_ex2 = ['#F58CF6', '#B6A2FC', '#3C5A99', '#EF473A', '#F38124', '#FFC900', '#33CD5F', '#11C1F3'];
      $scope.colors = [
        '#f2495e',
        '#f2994a',
        '#f2c94c',
        '#219653',
        '#2f80ed',
        '#56ccf2',
        '#bb6bd9',
        '#41b2af',
        '#df54a1',
        '#82c771'
      ];

      $scope.chartsGateways = [];
      $scope.chartsGatewaysView = []
      $scope.activeTab = 0
      $scope.tabLength = 2
      $scope.changeActiveTab = (index) => {
        $scope.activeTab = index
        if ($scope.activeTab === 1) { // Sensors tab
          getChartSensors();
          startTimeChartSensor();
          return;
        }
        clearInterval(timerChartSensor);
      }
      const startTimeChartSensor = () => {
        timerChartSensor = setInterval(() => {
          getChartSensors();
        }, 5000);
      }
      $scope.selectColor = (color) => $scope.selectedColor = color
      $scope.close = () => $state.go('menu.dashboards')
      $scope.sensors_datachart_piechart_sensors_statuses_options = {
        "legend": {
          "display": true,
          "position": 'right'
        },
        "animation": true,
      };


      mappingChartGatewayToView = (c) => {
        const labels = c.datasets.labels;
        const values = c.datasets.data;
        return {
          "labels": labels,
          "values": values,
          "deviceName": c.device.name,
          "id": c.id,
          "deviceUUID": c.device.uuid,
          "typeId": c.chartTypeId,
          "attribute": c.attribute,
          "currentSelectFilter": c.attribute.filters.length > 0 ? c.attribute.filters[0] : {}
        }
      }
      getChartGateways = () => {
        $http({
            method: 'GET',
            url: `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/gateways`,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            $scope.chartsGateways = result.data.data;
            $scope.chartsGatewaysView = $scope.chartsGateways.map((c) => mappingChartGatewayToView(c));
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      $scope.getChartGatewayDetail = (chartId, attributeId, filterId) => {

        console.log(`Filter chart by id ${chartId} ${attributeId} ${filterId}`);
        let url = `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/gateways/${chartId}`
        if (attributeId && filterId)
          url = `${url}?attributeId=${attributeId}&fiterId=${filterId}`;

        $http({
            method: 'GET',
            url: url,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            const chart = result.data.data;
            const foundIndex = $scope.chartsGatewaysView.findIndex((c) => c.id == chart.id);
            $scope.chartsGatewaysView[foundIndex] = mappingChartGatewayToView(chart);
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      $scope.save = () => {
        const request = {
          'name': $scope.dashboardDetail.name,
          'color': $scope.selectedColor
        };

        $http({
            method: 'PUT',
            url: `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}`,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
            data: request
          })
          .then(function (result) {
            console.log(result.data);
            $scope.getDashboards();
          })
          .catch(function (error) {
            console.error(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: 'Update dashboard was failed!',
            });
          });
      }

      $scope.addChart = (activeTab) => {
        switch (activeTab) {
          case 0:
            addNewChartGateway();
            return;
          case 1:
            addNewChartSensor();
            return;
        }
      }

      addNewChartSensor = () => {
        clearInterval(timerChartSensor);
        const params = {
          'dashboard': $scope.dashboardDetail,
          'dashboardId': $scope.dashboardDetail.id
        }
        $state.go('addNewChartSensor', params, {
          reload: true
        });
      };

      addNewChartGateway = () => {
        const params = {
          'dashboard': $scope.dashboardDetail,
          'dashboardId': $scope.dashboardDetail.id
        }
        $state.go('addNewChartGateway', params, {
          reload: true
        });
      }

      $scope.deleteChartGateway = (chartId) => {
        console.log("Chart ID: ", chartId)
        $ionicPopup.alert({
          title: 'Remove chart',
          template: 'Are you sure to remove it ?',
          buttons: [{
              text: 'Yes',
              type: 'button-positive',
              onTap: (e) => {
                $http({
                    method: 'DELETE',
                    url: `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/gateways/${chartId}`,
                    headers: {
                      'Authorization': 'Bearer ' + $scope.data.token.access,
                      'Content-Type': 'application/json'
                    }
                  })
                  .then(function (result) {
                    console.log(result.data);
                    $scope.chartsGatewaysView.splice($scope.chartsGatewaysView.findIndex((d) => d.id === chartId), 1)
                  })
                  .catch(function (error) {
                    console.error(error);
                    $ionicPopup.alert({
                      title: 'Dashboard',
                      template: 'Delete chart was failed!',
                    });
                  });
              }
            },
            {
              text: 'No',
              type: 'button-positive',
              onTap: (e) => true
            }
          ]
        });
      }

      $scope.selectFilter = (chartId, filterId) => {
        console.log("OK Try to test: " + chartId + "dsdasdas -- " + filterId);
      };

      getSensorColor = (sensorClass) => {
        switch (sensorClass) {
          case 'temperature':
            return ["#FFC900"];
          case 'humidity':
            return ['#F38124'];
          case 'Co2 gas':
            return ['#F58CF6'];
          case 'VOC gas':
            return ['#11C1F3'];
          case 'ambient light':
            return ['#B6A2FC'];
          case 'motion detection':
            return ['#3C5A99'];
        }

        return ["#FFC900"];
      }

      $scope.deleteChartSensor = (chartId) => {
        console.log("Chart ID: ", chartId)
        $ionicPopup.alert({
          title: 'Remove chart sensor',
          template: 'Are you sure to remove it ?',
          buttons: [{
              text: 'Yes',
              type: 'button-positive',
              onTap: (e) => {
                $http({
                    method: 'DELETE',
                    url: `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/sensors/${chartId}`,
                    headers: {
                      'Authorization': 'Bearer ' + $scope.data.token.access,
                      'Content-Type': 'application/json'
                    }
                  })
                  .then(function (result) {
                    console.log(result.data);
                    $scope.sensorsView.splice($scope.sensorsView.findIndex((d) => d.id === chartId), 1)
                  })
                  .catch(function (error) {
                    console.error(error);
                    $ionicPopup.alert({
                      title: 'Dashboard',
                      template: 'Delete chart was failed!',
                    });
                  });
              }
            },
            {
              text: 'No',
              type: 'button-positive',
              onTap: (e) => true
            }
          ]
        });
      }

      const selectedTimes = [{
          name: "5 minutes",
          value: 5
        },
        {
          name: "15 minutes",
          value: 15
        },
        {
          name: "30 minutes",
          value: 30
        },
        {
          name: "1 hour",
          value: 60
        }
      ];

      const getSelectedTime = (value) => {
        for (const i of selectedTimes) {
          if (i.value === value) {
            return i;
          }
        }
        return selectedTimes[0];
      }

      mapDataToSensorViews = (sensors) => {
        const result = sensors.map(c => {
          const dataset = c.dataset;
          labels = dataset.labels.map((timestamp) => {
            const date = new Date(timestamp * 1000);
            return ('0' + date.getHours()).slice(-2) +
              ":" + ('0' + date.getMinutes()).slice(-2) + ":" +
              ('0' + date.getSeconds()).slice(-2);
          });
          const lowAndHighs = [];
          for (let index = 0; index < dataset.high.length; index++) {
            const item = {
              "ticks": {
                "max": parseFloat(dataset.high[index]),
                "min": parseFloat(dataset.low[index]),
              }
            };
            lowAndHighs.push(item)
          }
          return {
            selectedTimes: selectedTimes,
            currentSelectTime: getSelectedTime(c.selectedMinutes),
            data: [dataset.data],
            labels: labels,
            device: c.device,
            id: c.id,
            chartType: c.chartTypeId,
            colors: getSensorColor(c.device.sensorClass),
            datasetOverride: [{
              label: c.device.sensorClass
            }],
            options: {
              "animation": false,
              "legend": {
                "display": true,
                "position": 'bottom'
              },
              "scales": {
                "xAxes": [{
                  "ticks": {
                    //"autoSkip": false,
                    "maxRotation": 90,
                    "minRotation": 90
                  }
                }]
              },
              legendCallback: function (chart) {
                // Return the HTML string here.
                console.log("Get LengendCallback: ,", chart);
                return "test";
              }
            }
          }
        });
        console.log("Result sensor: ", result);
        return result;
      };

      let chartIdsQueryParams = [];
      $scope.updateGetChartSensorsUrl = (minutes, chartId) => {
        if (chartIdsQueryParams.length == 0) {
          chartIdsQueryParams.push({
            minutes: minutes,
            chartId: chartId
          });
          return;
        } else {
          for (let index = 0; index < chartIdsQueryParams.length; index++) {
            const item = chartIdsQueryParams[index];
            if (item.chartId === chartId) {
              chartIdsQueryParams[index].minutes = minutes;
              chartIdsQueryParams[index].chartId = chartId;
              return;
            }
          }
        }
        chartIdsQueryParams.push({
          minutes: minutes,
          chartId: chartId
        });
      };

      buildChartsIdQueryParams = () => {
        let minutesParams = "&selected_minutues=";
        let chartIdsParams = "&chartsId=";

        for (let index = 0; index < chartIdsQueryParams.length; index++) {
          const item = chartIdsQueryParams[index];
          if (index == chartIdsQueryParams.length - 1) {
            minutesParams += `${item.minutes}`;
            chartIdsParams += `${item.chartId}`;
          } else {
            minutesParams += `${item.minutes},`;
            chartIdsParams += `${item.chartId},`;
          }

        }
        return `${minutesParams}${chartIdsParams}`;
      }

      getChartSensors = () => {
        let url = `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/sensors?minutes=5&points=30`
        if (chartIdsQueryParams.length != 0)
          url += buildChartsIdQueryParams();

        $http({
            method: 'GET',
            url: url,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            const charts = result.data.data
            $scope.sensors = charts;
            $scope.sensorsView = mapDataToSensorViews(charts);
            console.log("Chart Sensors: ", charts);
          })
          .catch(function (error) {
            console.log(error);
          });
      }



      $scope.compare = () => {
        const params = {
          'dashboardId': $scope.dashboardDetail.id,
          'charts': $scope.sensorsView.map(c => {
            return {
              'name': c.device.name,
              'id': c.id,
              'number': c.device.number,
              'source': c.device.source,
              'sensorClass': c.device.sensorClass,
              'gatewayUUID': c.device.gatewayUUID
            }
          })
        };

        $state.go('compareChartSensor', params, {
          reload: true
        });
        clearInterval(timerChartSensor);
      }

    }
  ])
  .controller('addDashboardCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;

      $scope.data = {
        'token': User.get_token(),
        'name': '',
        'selectedColor': '#f2495e',
        'colors': [
          '#f2495e',
          '#f2994a',
          '#f2c94c',
          '#219653',
          '#2f80ed',
          '#56ccf2',
          '#bb6bd9',
          '#41b2af',
          '#df54a1',
          '#82c771'
        ]
      };
      console.log("Name: ", $scope.data.name);
      $scope.selectColor = (color) => $scope.data.selectedColor = color

      $scope.close = () => $state.go('menu.dashboards')

      $scope.save = () => {
        const request = {
          'name': $scope.data.name,
          'color': $scope.data.selectedColor
        };

        $http({
            method: 'POST',
            url: server + '/dashboards',
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
            data: request
          })
          .then(function (result) {
            $scope.data.name = '';
            $scope.data.selectedColor = "#00c0ef";
            $state.go('menu.dashboards', {}, {
              reload: true
            })

          })
          .catch(function (error) {
            console.error(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: 'Create new dashboard was failed!',
            });
          });
      }
    }
  ])

  .controller('addNewChartGatewayCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;
      let dashboard = $stateParams.dashboard;
      $scope.close = () => $state.go('menu.dashboards')
      $scope.currentStep = 0;

      $scope.data = {
        'token': User.get_token(),
      }

      resest = () => {
        $scope.currentStep = 0;

        $scope.selectedGateway = {
          'deviceid': '',
          'devicename': ''
        };

        $scope.selectedAttribute = {
          'id': '',
          'name': ''
        };

        $scope.selectedChartType = {
          'id': '',
          'name': ''
        };
      }

      $scope.devicesGroups = [];
      $scope.attributes = [];
      $scope.chartTypes = [];

      // get gateways
      getGateways = () => {
        $http({
            method: 'GET',
            url: server + '/devicegroups/mixed',
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            const allDevices = result.data.data;
            $scope.devicesGroups = allDevices.devicegroups;
            devices = allDevices.devices;
            if (devices.length > 0) {
              deviceUngroup = {
                groupname: "Ungroup",
                devices: devices
              }
              $scope.devicesGroups.push(deviceUngroup);
            }
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      getAttributes = () => {
        $http({
            method: 'GET',
            url: server + '/dashboards/gateway/attributes'
          })
          .then(function (result) {
            $scope.attributes = result.data.data;
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      getChartTypes = () => {
        $http({
            method: 'GET',
            url: server + '/dashboards/charts/types/gateway',
          })
          .then(function (result) {
            $scope.chartTypes = result.data.data;
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      // Start the page
      $scope.$on('$ionicView.enter', (e) => {
        dashboard = $stateParams.dashboard;
        resest()
        getGateways();
        getAttributes();
        getChartTypes();
      });


      $scope.nextToAttributeStep = () => {
        if (!$scope.selectedGateway.deviceid) {
          $ionicPopup.alert({
            title: 'Select gateway',
            template: 'You have to select one gateway',
          });
          return;
        }
        $scope.currentStep = 1;

        // Set device name
        for (const group of $scope.devicesGroups) {
          for (const device of group.devices) {
            if (device.deviceid == $scope.selectedGateway.deviceid) {
              $scope.selectedGateway.devicename = device.devicename;
              return;
            }
          }
        }
      }

      $scope.backToGatewayStep = () => {
        $scope.currentStep = 0;
      }

      $scope.backToAttributeStep = () => {
        $scope.currentStep = 1;
      }

      $scope.nextToChartTypeStep = () => {
        if (!$scope.selectedAttribute.id) {
          $ionicPopup.alert({
            title: 'Select Attribute',
            template: 'You have to select one attribute',
          });
          return;
        }
        $scope.currentStep = 2;

        for (const attribute of $scope.attributes) {
          if (attribute.id == $scope.selectedAttribute.id) {
            $scope.selectedAttribute.name = attribute.name;
            return;
          }
        }
      }

      $scope.save = () => {
        console.log("dadsa")
        console.log(dashboard)
        if (!$scope.selectedChartType.id) {
          $ionicPopup.alert({
            title: 'Select ChartType',
            template: 'You have to select one chart type',
          });
          return;
        }
        const request = {
          "deviceId": $scope.selectedGateway.deviceid,
          "attributeId": parseInt($scope.selectedAttribute.id),
          "chartTypeId": parseInt($scope.selectedChartType.id)
        }

        $http({
            method: 'POST',
            url: `${server}/dashboards/dashboard/${dashboard.id}/gateways`,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
            data: request
          })
          .then(function (result) {
            resest()
            $state.go('menu.dashboards', {}, {
              reload: true
            })
          })
          .catch(function (error) {
            console.log(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: error.data.message,
            });
          });
      }
    }
  ])

  .controller('addNewChartSensorCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {
      const server = Server.rest_api;
      $scope.close = () => $state.go('menu.dashboards')
      let dashboard = $stateParams.dashboard;
      $scope.currentStep = 0;
      $scope.data = {
        'token': User.get_token(),
      }
      $scope.devicesGroups = [];
      $scope.sensors = [];
      $scope.chartTypes = [];
      let cachedSensors = [];

      reset = () => {
        $scope.currentStep = 0;
        $scope.selectedGateway = {
          'deviceid': '',
          'devicename': ''
        };

        $scope.selectedSensor = {
          'id': '',
          'sensorname': '',
          'source': '',
          'number': '',
        };

        $scope.selectedChartType = {
          'id': '',
          'name': ''
        };
      }

      $scope.nextToSellectionSensor = () => {
        const gatewayId = $scope.selectedGateway.deviceid;
        if (!$scope.selectedGateway.deviceid) {
          $ionicPopup.alert({
            title: 'Select gateway',
            template: 'You have to select one gateway',
          });
          return;
        }

        getSensors(gatewayId);
        $scope.currentStep = 1;
      }

      $scope.nextToChartTypeStep = () => {
        if (!$scope.selectedSensor.id) {
          $ionicPopup.alert({
            title: 'Select gateway',
            template: 'You have to select one gateway',
          });
          return;
        }
        getChartTypes();
        $scope.currentStep = 2;
      }

      $scope.backToSelectionSensorStep = () => {
        $scope.currentStep = 1;
      }

      $scope.backToGatewayStep = () => {
        $scope.currentStep = 0;
      }

      $scope.save = () => {
        if (!$scope.selectedChartType.id) {
          $ionicPopup.alert({
            title: 'Select ChartType',
            template: 'You have to select one chart type',
          });
          return;
        }

        const index = $scope.sensors.findIndex(s => s.id == $scope.selectedSensor.id);
        const sensor = $scope.sensors[index];
        const request = {
          "source": sensor.source,
          "number": sensor.number,
          "chartTypeId": parseInt($scope.selectedChartType.id)
        }

        $http({
            method: 'POST',
            url: `${server}/dashboards/dashboard/${dashboard.id}/sensors`,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
            data: request
          })
          .then(function (result) {
            reset()
            $state.go('menu.dashboards', {}, {
              reload: true
            })
          })
          .catch(function (error) {
            console.log(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: error.data.message,
            });
          });
      }
      // get gateways
      getGateways = () => {
        $http({
            method: 'GET',
            url: server + '/devicegroups/mixed',
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            const allDevices = result.data.data;
            $scope.devicesGroups = allDevices.devicegroups;
            devices = allDevices.devices;
            if (devices.length > 0) {
              deviceUngroup = {
                groupname: "Ungroup",
                devices: devices
              }
              $scope.devicesGroups.push(deviceUngroup);
            }
            console.log("Gateways: ", $scope.devicesGroups);
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      getSensors = (gatewayId) => {
        $http({
            method: 'GET',
            url: `${server}/gateways/${gatewayId}/sensors`,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            $scope.sensors = result.data.data;
            cachedSensors = $scope.sensors;
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      getChartTypes = () => {
        $http({
            method: 'GET',
            url: server + '/dashboards/charts/types/sensor',

          })
          .then(function (result) {
            $scope.chartTypes = result.data.data;
            console.log("ChartTypes: ", $scope.chartTypes);
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      $scope.$on('$ionicView.enter', (e) => {
        dashboard = $stateParams.dashboard;
        reset();
        getGateways();
      });
    }
  ])

  .controller('compareChartCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {
      const server = Server.rest_api;
      $scope.currentStep = 0;
      $scope.data = {
        'token': User.get_token(),
      }
      $scope.currentStep = 0;
      const charts = $stateParams.charts;
      const dashboardId = $stateParams.dashboardId;
      charts.forEach(c => {
        c.selected = false;
      });
      let timerChartSensor = {};

      $scope.charts = charts;
      $scope.comapreCharts = {};

      const startTimeChartSensor = () => {
        timerChartSensor = setInterval(() => {
          getChartsSensorsCompare();
        }, 5000);
      }

      $scope.$on("$ionicView.beforeLeave", function () {
        console.log("Clear timer of comparision");
        clearInterval(timerChartSensor);
      });

      getChartsIdQueryParams = (chartsId) => {
        let paramsChartsId = "&chartsId=";
        for (let index = 0; index < chartsId.length; index++) {
          const id = chartsId[index];
          if (index == chartsId.length - 1)
            paramsChartsId += id;
          else
            paramsChartsId += id + ","
        }
        return paramsChartsId;
      }

      $scope.close = () => {
        $scope.currentStep = 0;
        $scope.comapareCharts = {};
        $state.go('menu.dashboards');
      };
      $scope.back = () => {
        $scope.currentStep = 0;
        $scope.comapareCharts = {};
      }
      const selectedPoints = [
        {
          value: 30,
          name: '30 points'
        },
        {
          value: 60,
          name: '60 points'
        }
      ]
      let pointsQueryParam= 'points=30';
      $scope.currentSelectedPoints = selectedPoints[0];
      $scope.updatePointUrl = (point) => {
        pointsQueryParam = `points=${point}`;
        foundIndex = selectedPoints.findIndex(p => p.value == point);
        $scope.currentSelectedPoints = selectedPoints[foundIndex];
        currentSelectedPoints = point;

        clearInterval(timerChartSensor);
        getChartsSensorsCompare();
        startTimeChartSensor();
      }

      const selectedTimes = [{
          name: "5 minutes",
          value: 5,
        },
        {
          name: "15 minutes",
          value: 15
        },
        {
          name: "30 minutes",
          value: 30
        },
        {
          name: "1 hour",
          value: 60
        },
        {
          name: "1 day",
          value: 1440
        },
        {
          name: "1 week",
          value: 10080
        }
      ];

      const getSelectedTime = (value) => {
        for (const i of selectedTimes) {
          if (i.value === value) {
            return i;
          }
        }
        return selectedTimes[0];
      }

      let minuteQueryParams = "";
      let currentSelectedMinutes = 5;
      $scope.updateMinuteUrl = (minutes) => {
        minuteQueryParams = `&minutes=${minutes}`;
        currentSelectedMinutes = minutes;

        clearInterval(timerChartSensor);
        getChartsSensorsCompare();
        startTimeChartSensor();
      };

      $scope.compare = () => {
        getChartsSensorsCompare();
        startTimeChartSensor();
      }

      getChartsSensorsCompare = () => {
        const chartsId = $scope.charts.filter(c => c.selected)
          .map(c => c.id);
        let paramsChartsId = getChartsIdQueryParams(chartsId);
        let url = `${server}/dashboards/dashboard/${dashboardId}/sensors/comparison?${pointsQueryParam}${paramsChartsId}${minuteQueryParams}`;
        $http({
            method: 'GET',
            url: url,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            const charts = result.data.data
            console.log("Data Sensors Compare: ", charts);

            if (charts.length == 0) {
              return;
            }

            const labels = charts[0].dataset.labels.map((timestamp) => {
              const date = new Date(timestamp * 1000);
              return ('0' + date.getHours()).slice(-2) +
                ":" + ('0' + date.getMinutes()).slice(-2) + ":" +
                ('0' + date.getSeconds()).slice(-2);
            });


            const data = [];
            const datasetOverride = [];

            for (const chart of charts) {
              data.push(chart.dataset.data);
              datasetOverride.push({
                label: chart.device.sensorName
              })
            }

            $scope.comapareCharts = {
              selectedTimes: selectedTimes,
              currentSelectTime: getSelectedTime(currentSelectedMinutes),
              data: data,
              labels: labels,
              datasetOverride: datasetOverride,
              selectedPoints: selectedPoints,
              colors: [
                '#FFC900',
                '#F38124'
              ],
              options: {
                animation: false,
                legend: {
                  display: true,
                  position: 'bottom'
                },
                scales: {
                  xAxes: [{
                    ticks: {
                      //"autoSkip": false,
                      maxRotation: 90,
                      minRotation: 90
                    }
                  }]

                },
              }
            }

            $scope.currentStep = 1;
          })
          .catch(function (error) {
            clearInterval(timerChartSensor);
            console.log("Error ne : ", error);
            $ionicPopup.alert({
              title: 'Compare',
              template: `${error.data.message}`,
            });
          });
      }
    }
  ])
