angular.module('app.addNewChartGatewayCtrl', [])
  .controller('addNewChartGatewayCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;
      const dashboard = $stateParams.dashboard;
      $scope.dashboardDetail = dashboard;
      $scope.close = () => {
        const params = {
          'dashboard': $scope.dashboardDetail,
          'dashboardId': $scope.dashboardDetail.id,
          'activeTab': 1
        }
        $state.go('dashboardDetail', params, {
          reload: true
        });
      }
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
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
            $ionicPopup.alert({
              title: 'Dashboard',
              template: `${error.data.message}`,
            });
          });
      }

      // Start the page
      $scope.$on('$ionicView.enter', (e) => {
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
            resest();
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
    }
  ])
