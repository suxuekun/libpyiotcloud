angular.module('app.dashboardDetailCtrl', [])
  .controller('dashboardDetailCtrl', ['$scope', '$stateParams', '$state', '$filter', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $state, $filter, $ionicPopup, $http, Server, User, DateTimeUtil) {

      $scope.data = {
        'search': '',
        'token': User.get_token(),
      };
      const server = Server.rest_api;

      let timerChartSensor = {};
      const defaultColor = "#f2495e";
      const dashboard = $stateParams.dashboard;
      const activeTab = $stateParams.activeTab ? $stateParams.activeTab : 0;
      $scope.activeTab = activeTab;
      $scope.dashboardDetail = dashboard;
      $scope.selectedColor = $scope.dashboardDetail.color ? `${$scope.dashboardDetail.color}`: defaultColor;
      $scope.groupChartsGatewayView = {};
      $scope.chartsGateways  = [];
      $scope.chartsGatewaysView = [];

      $scope.$on('$ionicView.enter', (e) => {
        $scope.data.token = User.get_token();
        callChartsApi();
      });

      const callChartsApi = () => {
        stopTimeChartSensor();
        switch($scope.activeTab) {
          case 1: {
            getChartGateways();
            return;
          }
          case 2: {
            getChartSensors();
            startTimeChartSensor();
            return;
          }
        }
      }


      $scope.$on("$ionicView.beforeLeave", function () {
        console.log("Clear timer");
        stopTimeChartSensor();
        $scope.activeTab = 0
      });

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
      $scope.tabLength = 2
      $scope.changeActiveTab = (index) => {
        $scope.activeTab = index
        callChartsApi();
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

      $scope.getTotalSizeOfGroup = (groupCharts) => {
        let size = 0;
        groupCharts.forEach(charts => {
          size += charts.length;
        })
        return size;
      }

      const mapToGroupChartGatewayViews = () => {
        $scope.groupChartsGatewayView = {};
        $scope.chartsGatewaysView.forEach(c => {
          if (c.attribute.name in $scope.groupChartsGatewayView) {
            const groupCharts = $scope.groupChartsGatewayView[c.attribute.name];
            const charts = groupCharts[groupCharts.length - 1];
            if (charts.length < 3) {
              charts.push(c);
              groupCharts[groupCharts.length - 1] = charts;
            } else {
              const newCharts = [];
              newCharts.push(c);
              groupCharts.push(newCharts);
            }
            $scope.groupChartsGatewayView[c.attribute.name] = groupCharts;
          } else {
            $scope.groupChartsGatewayView[c.attribute.name] = [];
            const charts = [];
            charts.push(c);
            $scope.groupChartsGatewayView[c.attribute.name].push(charts);
          };
        });
        console.log("Group chart gateway: ", $scope.groupChartsGatewayView);
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
            mapToGroupChartGatewayViews();
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
            $scope.close();
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
          case 1:
            addNewChartGateway();
            return;
          case 2:
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
                    $scope.chartsGatewaysView.splice($scope.chartsGatewaysView.findIndex((d) => d.id === chartId), 1);
                    mapToGroupChartGatewayViews();
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
                    $scope.sensorsView.splice($scope.sensorsView.findIndex((d) => d.id === chartId), 1);
                    mapToGroupChartsSensorView();
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

      mapDataToSensorView = (c) => {
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
      }

      mapDataToSensorViews = (sensors) => {
        const result = sensors.map(c => {
          return mapDataToSensorView(c);
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

      const mapToGroupChartsSensorView = () => {
        $scope.groupChartsSensorView = {};
            $scope.sensorsView.forEach(c => {
              if (c.device.sensorClass in $scope.groupChartsSensorView) {
                const groupCharts = $scope.groupChartsSensorView[c.device.sensorClass];
                const charts = groupCharts[groupCharts.length - 1];
                if (charts.length < 2) {
                  charts.push(c);
                  groupCharts[groupCharts.length - 1] = charts;
                } else {
                  const newCharts = [];
                  newCharts.push(c);
                  groupCharts.push(newCharts);
                }
                $scope.groupChartsSensorView[c.device.sensorClass] = groupCharts;
              } else {
                $scope.groupChartsSensorView[c.device.sensorClass] = [];
                const charts = [];
                charts.push(c);
                $scope.groupChartsSensorView[c.device.sensorClass].push(charts);
              };
            });
            console.log("Group charts View: ",  $scope.groupChartsSensorView);
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
            mapToGroupChartsSensorView();
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
          'dashboard': $scope.dashboardDetail,
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

      $scope.getChartSensorDetail = (chartId) => {

        stopTimeChartSensor();
        const params = {
          'dashboard': $scope.dashboardDetail,
          'dashboardId': $scope.dashboardDetail.id,
          'chartId': chartId
        }
        $state.go('chartSensorDetail', params, {
          reload: true
        });

      }
    }
  ])
