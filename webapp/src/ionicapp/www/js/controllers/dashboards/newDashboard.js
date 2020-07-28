angular.module('app.addDashboardCtrl', [])
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

      $scope.close = () => $state.go('menu.dashboards', {}, {
        reload: true
      });

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
              template: `${error.data.message}`,
            });
          });
      }
    }
  ])
