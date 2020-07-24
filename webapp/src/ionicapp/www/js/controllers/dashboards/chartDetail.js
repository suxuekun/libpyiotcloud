angular.module('app.chartSensorDetailCtrl', [])
  .controller('chartSensorDetailCtrl', ['$scope', '$stateParams', '$filter', '$state', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $filter, $state, $ionicPopup, $http, Server, User, DateTimeUtil) {

      let timerChartSensor = {};

      const server = Server.rest_api;
      $scope.currentStep = 0;
      $scope.data = {
        'token': User.get_token(),
      }
      $scope.isRealTime = true;
      $scope.opacityOfHistoricalButton = 1;

      let currentTimestamp = DateTimeUtil.getCurrentTimestamp();

      const chartId = $stateParams.chartId;
      const dashboard = $stateParams.dashboard;
      $scope.dashboardDetail = dashboard;
      $scope.close = () => {
        const params = {
          'dashboard': $scope.dashboardDetail,
          'dashboardId': $scope.dashboardDetail.id,
          'activeTab': 2
        }
        $state.go('dashboardDetail', params, {
          reload: true
        });
      }

      let historiesDatasets = [];

      $scope.backToHistorical = () => {
        const chart = Object.assign($scope.chartDetail);
        historiesDatasets.push(chart);
        const currentTime = DateTimeUtil.convertTimestampToDate(currentTimestamp);
        const previousTime = DateTimeUtil.getPreviousTimestamp(currentTime, currentSelectedMinutes);
        currentTimestamp = previousTime;
        stopTimeChartSensor();
        getChartSensorDetail(previousTime);
      }

      $scope.nextToHistorical = () => {
        if (historiesDatasets.length == 0) {
          const current = DateTimeUtil.getCurrentTimestamp();
          if (current > currentTimestamp) {
            $scope.isRealTime = true;
            currentTimestamp = current;
            getChartSensorDetail(currentTimestamp);
            startTimeChartSensor();
          }
          return;
        }

        const chart = historiesDatasets.pop();
        $scope.chartDetail = chart;
      }

      const startTimeChartSensor = () => {
        timerChartSensor = setInterval(() => {
          currentTimestamp = DateTimeUtil.getCurrentTimestamp();
          getChartSensorDetail(currentTimestamp);
        }, 5000);
      }

      const stopTimeChartSensor = () => {
        clearInterval(timerChartSensor);
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

      const selectedPoints = [{
          value: 30,
          name: '30 points'
        },
        {
          value: 60,
          name: '60 points'
        }
      ]

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
        const labels = datasets.labels.map((t) => {
          const date = new Date(t * 1000);
          return ('0' + date.getHours()).slice(-2) +
            ":" + ('0' + date.getMinutes()).slice(-2) + ":" +
            ('0' + date.getSeconds()).slice(-2);
        });
        return labels;
      }

      let currentSelectedMinutes = 5;
      let minuteQueryParams = "minutes=5";
      $scope.updateMinuteUrl = (minutes) => {
        minuteQueryParams = `minutes=${minutes}`;
        currentSelectedMinutes = minutes;
        stopTimeChartSensor();
        getChartSensorDetail(currentTimestamp);
        if ($scope.isRealTime)
          startTimeChartSensor();
      };

      let pointsQueryParam = 'points=30';
      let currentSelectedPoints = selectedPoints[0];
      $scope.updatePointUrl = (point) => {
        pointsQueryParam = `points=${point}`;
        foundIndex = selectedPoints.findIndex(p => p.value == point);
        currentSelectedPoints = selectedPoints[foundIndex];

        stopTimeChartSensor();
        getChartSensorDetail(currentTimestamp);
        if ($scope.isRealTime)
          startTimeChartSensor();
      }

      $scope.$on("$ionicView.beforeLeave", function () {
        console.log("Clear timer of comparision");
        stopTimeChartSensor();
        $scope.chartDetail = {};
      });

      $scope.$on('$ionicView.enter', (e) => {
        getChartSensorDetail(currentTimestamp);
        startTimeChartSensor();
      });

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
          currentSelectedPoints: currentSelectedPoints,
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
          selectedPoints: selectedPoints,
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

      const getChartSensorDetail = (timestamp) => {
        if (!timestamp)
          timestamp = DateTimeUtil.getCurrentTimestamp();

        let url = `${server}/dashboards/dashboard/${dashboard.id}/sensors/${chartId}?timestamp=${timestamp}&${pointsQueryParam}&${minuteQueryParams}`;
        console.log("Url: ", url);

        $http({
            method: 'GET',
            url: url,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            }
          })
          .then(function (result) {
            const chart = result.data.data;
            console.log("Get n ew sata ne ", chart);
            $scope.chartDetail = mapDataToSensorView(chart);
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
