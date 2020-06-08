angular.module('app.dashboardsCtrl', [])
  .controller('dashboardsCtrl', ['$scope', '$stateParams', '$state', '$filter', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $state, $filter, $ionicPopup, $http, Server, User, DateTimeUtil) {

      const server = Server.rest_api;
      let cachedDashboards = [];
      $scope.$on('$ionicView.enter', (e) => {
        getDashboards();
      });

      $scope.add = () => {
        const device_param = {}
        $state.go('addDashboard', device_param);
      }

      $scope.delete = (id) => {
        $ionicPopup.alert({
          title: 'Remove dashboard',
          template: 'Are you sure to remove it ?',
          buttons: [
            {
              text: 'Yes',
              type: 'button-positive',
              onTap: function (e) {
                $http({
                  method: 'DELETE',
                  url: `${server}/dashboards/${id}`,
                  headers: { 'Content-Type': 'application/json' }
                })
                  .then(function (result) {
                    console.log(result.data);
                    const dashboards = $scope.dashboards
                    cachedDashboards.splice(dashboards.findIndex((d) => d.id === id), 1)
                    $scope.dashboards.splice(dashboards.findIndex((d) => d.id === id), 1);
                  })
                  .catch(function (error) {
                    console.error(error);
                    $ionicPopup.alert({
                      title: 'Dashboard',
                      template: 'Delete dashboard failed!',
                    });
                  });
                //$state.go('menu.organizations', param, {reload:true} );
              }
            }
          ]
        });
      }

      $scope.viewDetail = (dashboard) => {

        const params = {
          'dashboard': dashboard,
          'dashboardId': dashboard.id
        }
        $state.go('updateDashboard', params, { reload: true })
      }


      // Init private functions
      renderDashdoards = (dashboards) => {
        $scope.dashboards = dashboards.map((d) => {
          return {
            id: d.id,
            color: d.color,
            name: d.name,
            createdAt: $filter('date')(DateTimeUtil.convertTimestampToDate(d.createdAt), "dd/MM/yyyy hh:mm"),
            modifiedAt: $filter('date')(DateTimeUtil.convertTimestampToDate(d.modifiedAt), "dd/MM/yyyy hh:mm")
          }
        });
      }

      getDashboards = () => {
        $http({
          method: 'GET',
          url: server + '/dashboards',
          headers: { 'Content-Type': 'application/json' },
        })
          .then(function (result) {
            cachedDashboards = result.data.data;
            renderDashdoards(cachedDashboards);
          })
          .catch(function (error) {
            console.log(error);
          });
      }

    }
  ])
  .controller('addDashboardCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;

      $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'name': ''
      };

      $scope.close = () => $state.go('dashboards')


      $scope.save = () => {
        const request = {
          'name': $scope.data.name,
          'color': "Black"
        };

        $http({
          method: 'POST',
          url: server + '/dashboards',
          headers: { 'Content-Type': 'application/json' },
          data: request
        })
          .then(function (result) {
            console.log(result.data);
            $state.go('menu.dashboards', {}, { reload: true })
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

  .controller('updateDashboardCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;
      const dashboard = $stateParams.dashboard

      $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'name': dashboard.name,
      };


      $scope.close = () => $state.go('dashboards')

      $scope.save = () => {
        console.log("Dashboard name: ", $scope.data.name);
        const request = {
          'name': $scope.data.name,
          'color': "Black"
        };

        $http({
          method: 'PUT',
          url: `${server}/dashboards/${dashboard.id}`,
          headers: { 'Content-Type': 'application/json' },
          data: request
        })
          .then(function (result) {
            console.log(result.data);
            $state.go('menu.dashboards', {}, { reload: true })
          })
          .catch(function (error) {
            console.error(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: 'Update dashboard was failed!',
            });
          });
      }
    }
  ])
