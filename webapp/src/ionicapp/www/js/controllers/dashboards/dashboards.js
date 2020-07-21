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
        stopTimeChartSensor();

        $scope.dashboardDetail = {};
        $scope.chartsGatewaysView = [];
        $scope.sensorsView = [];
        $scope.activeTab = 0

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
      $scope.isRealTime = true;

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
        stopTimeChartSensor();
        $scope.chartsGatewaysView = [];
        $scope.sensorsView = [];
        $scope.dashboardDetail = dashboard;
        $scope.selectedColor = $scope.dashboardDetail.color ? `${$scope.dashboardDetail.color}` : defaultColor;
        switch ($scope.activeTab) {
          case 0:
            getChartGateways();
            return;
          case 1:
            getChartSensors($scope.isRealTime);
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
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
      $scope.chartsGatewaysView = [];
      $scope.sensorsView = [];
      $scope.activeTab = 0
      $scope.tabLength = 2
      $scope.changeActiveTab = (index) => {
        $scope.activeTab = index
        if ($scope.activeTab === 1) { // Sensors tab
          getChartSensors($scope.isRealTime);
          startTimeChartSensor();
          return;
        }
        stopTimeChartSensor();
      }
      const startTimeChartSensor = () => {
        timerChartSensor = setInterval(() => {
          getChartSensors(true);
        }, 5000);
      }

      const stopTimeChartSensor = () => {
        clearInterval(timerChartSensor);
      }

      $scope.selectColor = (color) => $scope.selectedColor = color
      $scope.close = () => $state.go('menu.dashboards', {}, {
        reload: true
      });
      $scope.sensors_datachart_piechart_sensors_statuses_options = {
        "legend": {
          "display": true,
          "position": 'right'
        },
        "animation": true,
      };

      $scope.selectFilter = (chartId, attributeId, filterId) => {
        const index = $scope.chartsGatewaysView.findIndex((c) => c.id == chartId);
        chart = $scope.chartsGatewaysView[index];
        const datasetIndex = chart.datasets.findIndex((d) => d.filterId == filterId);
        chart.selectedDataset = chart.datasets[datasetIndex];

      };

      mappingChartGatewayToView = (c) => {
        const selectedDataset = c.datasets[0];
        const datasets = c.datasets;
        return {
          datasets: datasets,
          selectedDataset: selectedDataset,
          deviceName: c.device.name,
          id: c.id,
          deviceUUID: c.device.uuid,
          typeId: c.chartTypeId,
          attribute: c.attribute,
          currentSelectFilter: c.attribute.filters.length > 0 ? c.attribute.filters[0] : {}
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });

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
              template: `${error.data.message}`,
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
        stopTimeChartSensor();
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
      mapLabelsOfDatasets = (datasets) => {
        const labels = datasets.labels.map((timestamp) => {
          const date = new Date(timestamp * 1000);
          return ('0' + date.getHours()).slice(-2) +
            ":" + ('0' + date.getMinutes()).slice(-2) + ":" +
            ('0' + date.getSeconds()).slice(-2);
        });
        return labels;
      }

      mapDataToSensorViews = (sensors) => {
        console.log("Charts: ", sensors);
        const result = sensors.map(c => {
          const datasets = c.datasets;
          const labels = mapLabelsOfDatasets(datasets);
          const lowAndHighs = [];
          for (let index = 0; index < datasets.high.length; index++) {
            const item = {
              "ticks": {
                "max": parseFloat(datasets.high[index]),
                "min": parseFloat(datasets.low[index]),
              }
            };
            lowAndHighs.push(item)
          }
          return {
            selectedTimes: selectedTimes,
            currentSelectTime: getSelectedTime(c.selectedMinutes),
            oldDatasets: c.oldDatasets,
            datasets: c.datasets,
            data: [datasets.data],
            labels: labels,
            device: c.device,
            id: c.id,
            chartType: c.chartTypeId,
            colors: getSensorColor(c.device.sensorClass),
            currentTimespan: 0,
            datasetOverride: [{
              label: c.device.sensorClass
            }],
            readings: c.readings,
            typeId: c.chartTypeId,
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
              tooltips: {
                enabled: true,
                callbacks: {
                  title: function (tooltipItem, data) {
                    // console.log("Dasd adas dassadaa :", c.device);
                    return c.device.sensorName;
                  },
                  label: function (tooltipItem, data) {
                    return ' ' + data.datasets[tooltipItem.datasetIndex].label + ' ' + tooltipItem.yLabel;
                  }
                }
              },
            },

          }
        });
        return result;
      };

      let chartIdsQueryParams = [];
      $scope.updateGetChartSensorsUrl = (minutes, chartId) => {
        if (chartIdsQueryParams.length == 0) {
          chartIdsQueryParams.push({
            minutes: minutes,
            chartId: chartId
          });
          stopTimeChartSensor();
          getChartSensors($scope.isRealTime);
          startTimeChartSensor();
          return;
        } else {
          for (let index = 0; index < chartIdsQueryParams.length; index++) {
            const item = chartIdsQueryParams[index];
            if (item.chartId === chartId) {
              chartIdsQueryParams[index].minutes = minutes;
              chartIdsQueryParams[index].chartId = chartId;
              stopTimeChartSensor();
              getChartSensors($scope.isRealTime);
              startTimeChartSensor();
              return;
            }
          }
        }
        chartIdsQueryParams.push({
          minutes: minutes,
          chartId: chartId
        });
        stopTimeChartSensor();
        getChartSensors($scope.isRealTime);
        startTimeChartSensor();
      };

      buildChartsIdQueryParams = () => {
        let minutesParams = "&selected_minutes=";
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

      $scope.backToHistorical = (chart, currentTimespan) => {
        if ($scope.isRealTime) {
          $ionicPopup.alert({
            title: 'Dashboard',
            template: "Sorry you have to disable realtime",
          });
          return;
        }
        if (!chart.oldDatasets) {
          console.log("OldDatasets is undefined");
          return;
        }

        if (currentTimespan == chart.oldDatasets.length) {
          $ionicPopup.alert({
            title: 'Dashboard',
            template: "Sorry we just support 3 times historicals",
          });
          return;
        }
        const datasets = chart.oldDatasets[currentTimespan];
        chart.currentTimespan = currentTimespan + 1;
        chart.data = [datasets.data];
        const labels = mapLabelsOfDatasets(datasets);
        chart.labels = labels;
      };

      $scope.opacityOfHistoricalButton = 0.5;
      $scope.nextToHistorical = (chart, currentTimespan) => {
        if ($scope.isRealTime) {
          $ionicPopup.alert({
            title: 'Dashboard',
            template: "Sorry you have to disable realtime",
          });
          return;
        }

        if (!chart.oldDatasets) {
          console.log("OldDatasets is undefined");
          return;
        }

        if (currentTimespan == 0) {
          // Update datasets is current time
          const datasets = chart.datasets;
          chart.data = [datasets.data];
          chart.labels = mapLabelsOfDatasets(datasets);
          chart.currentTimespan = 0;

          return;
        }
        const timespan = currentTimespan - 1;
        chart.currentTimespan = timespan;
        const datasets = chart.oldDatasets[timespan];
        chart.data = [datasets.data];
        chart.labels = mapLabelsOfDatasets(datasets);
      };

      $scope.toggelRealTime = () => {
        $scope.isRealTime = !$scope.isRealTime;
        if ($scope.isRealTime) {
          $scope.opacityOfHistoricalButton = 0.5;
          startTimeChartSensor();
          return;
        }
        $scope.opacityOfHistoricalButton = 1;
        stopTimeChartSensor();
        getChartSensors(false);
        // Start get api again
      }

      getChartSensors = (realTime = true) => {
        let url = `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/sensors?minutes=5`;
        if (!realTime)
          url = `${server}/dashboards/dashboard/${$scope.dashboardDetail.id}/sensors?realtime=false&timespan=3`;

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
            $scope.sensorsView = mapDataToSensorViews(charts);

            $scope.groupChartsSensorView = {};
            $scope.sensorsView.forEach(c => {

              if (c.device.sensorClass in $scope.groupChartsSensorView) {
                $scope.groupChartsSensorView[c.device.sensorClass].push(c);
              } else {
                $scope.groupChartsSensorView[c.device.sensorClass] = [];
                $scope.groupChartsSensorView[c.device.sensorClass].push(c);
              };
            });


          })
          .catch(function (error) {
            console.log(error);
            stopTimeChartSensor();
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
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
              'gatewayUUID': c.device.gatewayUUID,
              'gatewayName': c.device.gatewayName
            }
          })
        };

        $state.go('compareChartSensor', params, {
          reload: true
        });
        stopTimeChartSensor();
      }

    }
  ])
