angular.module('app.addNewChartSensorCtrl', [])
  .controller('addNewChartSensorCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {
      const server = Server.rest_api;
      $scope.close = () => $state.go('menu.dashboards', {}, {
        reload: true
      });
      let dashboard = $stateParams.dashboard;
      $scope.currentStep = 0;
      $scope.data = {
        'token': User.get_token(),
      }
      $scope.devicesGroups = [];
      $scope.chartTypes = [];
      $scope.sensorsView = [];
      $scope.groupChartsSensorView = {};

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
        const gatewayName = $scope.selectedGateway.devicename;
        if (!gatewayName) {
          $ionicPopup.alert({
            title: 'Select gateway',
            template: 'You have to select one gateway',
          });
          return;
        }

        getSensors(gatewayName);
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
            $scope.close();
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
          });
      }

      getSensors = (gatewayName) => {
        $http({
            method: 'GET',
            url: `${server}/devices/device/${gatewayName}/ldsbus/0/sensors`,
            headers: {
              'Authorization': 'Bearer ' + $scope.data.token.access,
              'Content-Type': 'application/json'
            },
          })
          .then(function (result) {
            sensors = result.data.sensors;
            $scope.sensors = sensors.map((s) => {
              return {
                id: `${s.source}-${s.number}`,
                sensorname: s.sensorname,
                enabled: s.enabled,
                class: s.class,
                port: s.port,
                number: s.number,
                source: s.source,
                deviceid: s.deviceid,
              }
            });
          })
          .catch(function (error) {
            console.log(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
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
