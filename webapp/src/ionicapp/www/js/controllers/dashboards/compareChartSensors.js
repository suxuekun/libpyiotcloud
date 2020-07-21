angular.module('app.compareChartCtrl', [])
  .controller('compareChartCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {
      const server = Server.rest_api;
      $scope.currentStep = 0;
      $scope.data = {
        'token': User.get_token(),
      }
      $scope.currentStep = 0;
      $scope.isRealTime = true;



      const charts = $stateParams.charts;
      const dashboardId = $stateParams.dashboardId;

      $scope.dictCharts = {};
      charts.forEach(c => {
        c.selected = false;
        if (c.sensorClass in $scope.dictCharts) {
          $scope.dictCharts[c.sensorClass].push(c);
        } else {
          $scope.dictCharts[c.sensorClass] = [];
          $scope.dictCharts[c.sensorClass].push(c);
        };
      });

      let timerChartSensor = {};

      $scope.charts = charts;
      $scope.comapreCharts = {};

      const startTimeChartSensor = () => {
        timerChartSensor = setInterval(() => {
          getChartsSensorsCompare();
        }, 5000);
      }

      const stopTimeChartSensor = () => {
        clearInterval(timerChartSensor);
      }

      $scope.$on("$ionicView.beforeLeave", function () {
        console.log("Clear timer of comparision");
        stopTimeChartSensor();
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
        $state.go('menu.dashboards', {}, {
          reload: true
        });
      };
      $scope.back = () => {
        stopTimeChartSensor();
        $scope.currentStep = 0;
        $scope.comapareCharts = {};
        $scope.currentSelectedPoints = selectedPoints[0];
      }
      const selectedPoints = [{
          value: 30,
          name: '30 points'
        },
        {
          value: 60,
          name: '60 points'
        }
      ]

      let pointsQueryParam = 'points=30';
      let currentSelectedPoints = selectedPoints[0];

      const resetPointQueryParam = () => {
        pointsQueryParam = 'points=30';
        currentSelectedPoints = selectedPoints[0];
      }

      $scope.updatePointUrl = (point) => {
        pointsQueryParam = `points=${point}`;
        foundIndex = selectedPoints.findIndex(p => p.value == point);
        currentSelectedPoints = selectedPoints[foundIndex];

        stopTimeChartSensor();
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

        stopTimeChartSensor();
        getChartsSensorsCompare();
        startTimeChartSensor();
      };

      $scope.compare = () => {
        console.log("Compare: ", currentSelectedPoints);
        resetPointQueryParam();
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

            const labels = charts[0].datasets.labels.map((timestamp) => {
              const date = new Date(timestamp * 1000);
              return ('0' + date.getHours()).slice(-2) +
                ":" + ('0' + date.getMinutes()).slice(-2) + ":" +
                ('0' + date.getSeconds()).slice(-2);
            });


            const data = [];
            const datasetOverride = [];

            for (const chart of charts) {
              data.push(chart.datasets.data);
              datasetOverride.push({
                label: chart.device.sensorName
              })
            }

            $scope.comapareCharts = {
              selectedTimes: selectedTimes,
              currentSelectedPoints: currentSelectedPoints,
              currentSelectTime: getSelectedTime(currentSelectedMinutes),
              data: data,
              labels: labels,
              datasetOverride: datasetOverride,
              selectedPoints: selectedPoints,
              colors: [
                // ['#FFC900'],
                // ['#F38124'],
                // ['#B6A2FC'],
                '#FFC900',
                '#F38124',
                '#B6A2FC',
                '#3C5A99',
                '#11C1F3'
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
            stopTimeChartSensor();
            console.log("Error ne : ", error);
            $ionicPopup.alert({
              title: 'Compare',
              template: `${error.data.message}`,
            });
          });
      }
    }
  ])
