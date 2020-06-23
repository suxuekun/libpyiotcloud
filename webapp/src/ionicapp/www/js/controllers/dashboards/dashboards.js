angular.module('app.dashboardsCtrl', [])
  .controller('dashboardsCtrl', ['$scope', '$stateParams', '$state', '$filter', '$ionicPopup', '$http', 'Server', 'User', 'DateTimeUtil',
    function ($scope, $stateParams, $state, $filter, $ionicPopup, $http, Server, User, DateTimeUtil) {

      $scope.data = {
        'search': '',
        'token': User.get_token(),
      };

      $scope.dashboardDetail = {};

      const server = Server.rest_api;
      let cachedDashboards = [];

      // Start the page
      $scope.$on('$ionicView.enter', (e) => {
        $scope.data.token = User.get_token();
        $scope.getDashboards();
      });

      // Init life cycle
      $scope.add = () => {
        const device_param = {}
        $state.go('addDashboard', device_param, { reload: true });
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
          buttons: [
            {
              text: 'Yes',
              type: 'button-positive',
              onTap: (e) => {
                $http({
                  method: 'DELETE',
                  url: `${server}/dashboards/${id}`,
                  headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' }
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
        $scope.dashboardDetail = dashboard;
        console.log("View Detail ",  $scope.dashboardDetail);
        $scope.selectedColor = $scope.dashboardDetail.color ? `${$scope.dashboardDetail.color}` : defaultColor;
        getChartGateways();
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
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
        })
          .then(function (result) {
            cachedDashboards = result.data.data;
            renderDashdoards(cachedDashboards);
            if (cachedDashboards.length > 0) {
              $scope.dashboardDetail = cachedDashboards[0];
              getChartGateways();
            }
          })
          .catch(function (error) {
            console.log(error);
          });
      }
      // Scope of dashboard detail
      $scope.sensors_datachart_colors_options_ex = ['#EF473A', '#F38124', '#FFC900', '#33CD5F', '#11C1F3', '#3C5A99', '#B6A2FC', '#F58CF6'];
      $scope.colors = [
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
      ];

      const defaultColor = "#00c0ef";
      $scope.selectedColor = defaultColor;
      $scope.chartsGateways = [];
      $scope.chartsGatewaysView = []
      $scope.activeTab = 0
      $scope.tabLength = 2
      $scope.changeActiveTab = (index) => {
        $scope.activeTab = index
      }
      $scope.selectColor = (color) => $scope.selectedColor = color
      $scope.close = () => $state.go('menu.dashboards')
      $scope.sensors_datachart_piechart_sensors_statuses_options = {
        "legend": {
          "display": true,
          "position": 'right'
        }
      };

      getChartGateways = () => {
        $http({
          method: 'GET',
          url: `${server}/dashboards/${$scope.dashboardDetail.id}/gateways`,
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
        })
          .then(function (result) {
            console.log(result.data.data);
            $scope.chartsGateways = result.data.data;
            $scope.chartsGatewaysView = $scope.chartsGateways.map((c) => {
              labels = c.datasets.map((d) => d.name);
              values = c.datasets.map((d) => d.value);
              return {
                "labels": labels,
                "values": values,
                "deviceName": c.device.name,
                "id": c.id,
                "deviceUUID": c.device.uuid,
                "typeId": c.typeId,
                "attribute": c.attribute,
                "currentSelectFilter": c.attribute.filters.length > 0 ? c.attribute.filters[0] : {}
              }
            });
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      $scope.getChartGatewayDetail = (chartId, attributeId, filterId) => {

        console.log(`Filter chart by id ${chartId} ${attributeId} ${filterId}`);
        let url = `${server}/dashboards/${$scope.dashboardDetail.id}/gateways/${chartId}`
        if (attributeId && filterId)
          url = `${url}?attributeId=${attributeId}&fiterId=${filterId}`;

        $http({
          method: 'GET',
          url: url,
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
        })
          .then(function (result) {
            console.log(result.data.data);
          })
          .catch(function (error) {
            console.log(error);
          });
      }

      $scope.save = () => {
        const request = {
          'name': $scope.dashboardDetail.name,
          'color': $scope.selectedColor
        };

        $http({
          method: 'PUT',
          url: `${server}/dashboards/${$scope.dashboardDetail.id}`,
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
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
              template: 'Update dashboard was failed!',
            });
          });
      }

      $scope.addNewChartGateway = () => {
        const params = {
          'dashboard': $scope.dashboardDetail,
          'dashboardId': $scope.dashboardDetail.id
        }
        $state.go('addNewChartGateway', params,  { reload: true });
      }

      $scope.deleteChartGateway = (chartId) => {
        console.log("Chart ID: ", chartId)
        $ionicPopup.alert({
          title: 'Remove chart',
          template: 'Are you sure to remove it ?',
          buttons: [
            {
              text: 'Yes',
              type: 'button-positive',
              onTap: (e) => {
                $http({
                  method: 'DELETE',
                  url: `${server}/dashboards/${$scope.dashboardDetail.id}/gateways/${chartId}`,
                  headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' }
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

      $scope.selectFilter = (chartId, filterId) => {
        console.log("OK Try to test: " + chartId + "dsdasdas -- " + filterId);
      };
    }
  ])
  .controller('addDashboardCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;

      $scope.data = {
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
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
          data: request
        })
          .then(function (result) {
            $scope.data.name = '';
            $scope.data.selectedColor = "#00c0ef";
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

  .controller('addNewChartGatewayCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User',
    function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

      const server = Server.rest_api;
      let dashboard = $stateParams.dashboard;
      $scope.close = () => $state.go('menu.dashboards')
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
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
        })
          .then(function (result) {
            const allDevices = result.data.data;
            $scope.devicesGroups = allDevices.devicegroups;
            devices = allDevices.devices;

            if (devices.length > 0) {
              deviceUngroup = {
                groupname: "Ungroup",
                devicesInfo: devices
              }
              $scope.devicesGroups.push(deviceUngroup);
            }
          })
          .catch(function (error) {
            console.log(error);
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
          });
      }

      // Start the page
      $scope.$on('$ionicView.enter', (e) => {
        dashboard = $stateParams.dashboard;
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
          for (const device of group.devicesInfo) {
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
          "gatewayId": $scope.selectedGateway.deviceid,
          "attributeId": parseInt($scope.selectedAttribute.id),
          "chartTypeId": parseInt($scope.selectedChartType.id)
        }

        $http({
          method: 'POST',
          url: `${server}/dashboards/${dashboard.id}/gateways`,
          headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
          data: request
        })
          .then(function (result) {
            resest()
            $state.go('menu.dashboards', {}, { reload: true })
          })
          .catch(function (error) {
            console.log(error);
            $ionicPopup.alert({
              title: 'Dashboard',
              template: 'Create new dashboard was failed!',
            });
          });
      }
    }
  ])
