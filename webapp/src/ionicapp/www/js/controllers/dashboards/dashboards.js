angular.module('app.dashboardsCtrl', [])
  .controller('dashboardsCtrl', ['$scope', '$stateParams', '$state', '$filter', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $state, $filter, $ionicPopup, $http, Server, User, DateTimeUtil) {

      $scope.data = {
        'search': '',
        'token': User.get_token(),
      };

      const server = Server.rest_api;
      let cachedDashboards = [];

      // Start the page
      $scope.$on('$ionicView.enter', (e) => {
        $scope.data.token = User.get_token();
        getDashboards();
      });

      $scope.$on("$ionicView.beforeLeave", function () {
        console.log("Clear timer");
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
        const params = {
          dashboardId: dashboard.id,
          dashboard: dashboard
        }
        $state.go('dashboardDetail', params, {
          reload: true,
          cached: false
        });
      }

      const getDashboards = () => {
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

      // Init private functions
      renderDashdoards = (dashboards) => {
        $scope.dashboards = dashboards.map((d) => {
          return {
            id: d.id,
            color: `#${d.color}`,
            name: d.name,
            totalGateways: d.totalGateways,
            totalSensors: d.totalSensors,
            totalActuators: d.totalActuators,
            createdAt: $filter('date')(DateTimeUtil.convertTimestampToDate(d.createdAt), "dd/MM/yyyy hh:mm"),
            modifiedAt: $filter('date')(DateTimeUtil.convertTimestampToDate(d.modifiedAt), "dd/MM/yyyy hh:mm")
          }
        });
      }
    }
  ])
