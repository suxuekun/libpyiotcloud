angular.module('app.dashboardsCtrl', [])
  .controller('dashboardsCtrl', ['$scope', '$stateParams', '$state', '$filter', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $state, $filter, $ionicPopup, $http, Server, User, DateTimeUtil) {

      $scope.data = {
        'search': ''
      };

      const server = Server.rest_api;
      let cachedDashboards = [];
      $scope.$on('$ionicView.enter', (e) => {
        getDashboards();
      });

      $scope.add = () => {
        const device_param = {}
        $state.go('addDashboard', device_param, { reload: true });
      }

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
          buttons: [
            {
              text: 'Yes',
              type: 'button-positive',
              onTap: (e) => {
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
        'name': '',
        'selectedColor': '#00c0ef',
        'colors': [
          '#00c0ef',
          '#0073b7',
          '#3c8dbc',
          '#39CCCC',
          '#f39c12',
          '#FF851B',
          '#00a65a',
          '#01FF70',
          '#dd4b39',
          '#605ca8',
          '#F012BE'
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
          headers: { 'Content-Type': 'application/json' },
          data: request
        })
          .then(function (result) {
            console.log(result.data);
            $scope.data.name = '';
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
        'selectedColor': dashboard.color ? dashboard.color : '#00c0ef',
        'colors': [
          '#00c0ef',
          '#0073b7',
          '#3c8dbc',
          '#39CCCC',
          '#f39c12',
          '#FF851B',
          '#00a65a',
          '#01FF70',
          '#dd4b39',
          '#605ca8',
          '#F012BE'
        ]
      };

      $scope.selectColor = (color) => $scope.data.selectedColor = color

      $scope.close = () => $state.go('menu.dashboards')

      $scope.save = () => {
        console.log("Dashboard name: ", $scope.data.name);
        const request = {
          'name': $scope.data.name,
          'color': $scope.data.selectedColor
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
