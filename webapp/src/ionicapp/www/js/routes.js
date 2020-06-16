angular.module('app.routes', [])

  .config(function ($stateProvider, $urlRouterProvider) {

    // Ionic uses AngularUI Router which uses the concept of states
    // Learn more here: https://github.com/angular-ui/ui-router
    // Set up the various states which the app can be in.
    // Each state's controller can be found in controllers.js
    $stateProvider


      .state('home', {
        url: '/page_home',
        templateUrl: 'templates/home.html',
        controller: 'homeCtrl'
      })
      .state('menu.dashboards', {
        url: '/dashboards',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/dashboards1.html',
            controller: 'dashboardsCtrl'
          }
        }
      })

      .state('addDashboard', {
        url: '/dashboard_register',
        params: {
          username: "",
          token: "",
        },
        templateUrl: 'templates/addDashboard.html',
        controller: 'addDashboardCtrl'
      })

      .state('updateDashboard', {
        url: '/dashboard/{dashboardId}',
        params: {
          username: "",
          token: "",
          dashboard: {}
        },
        templateUrl: 'templates/dashboardDetail.html',
        controller: 'updateDashboardCtrl'
      })

      .state('menu.gateways', {
        url: '/page_devices',
        params: {
          username: "",
          token: "",
          activeSection: "1"
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/gateways.html',
            controller: 'gatewaysCtrl'
          }
        }
      })

      .state('menu.profile', {
        url: '/page_profile',
        params: {
          username: "",
          token: "",
          activeSection: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/profile.html',
            controller: 'profileCtrl'
          }
        }
      })

      .state('menu.credits', {
        url: '/page_credits',
        params: {
          username: "",
          token: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/credits.html',
            controller: 'creditsCtrl'
          }
        }
      })

      .state('topUpCredits', {
        url: '/page_topup',
        params: {
          username: "",
          token: "",
          credits: ""
        },
        templateUrl: 'templates/topUpCredits.html',
        controller: 'topUpCreditsCtrl'
      })

      .state('creditPurchases', {
        url: '/page_credit_purchases',
        params: {
          username: "",
          token: "",
          credits: ""
        },
        templateUrl: 'templates/creditPurchases.html',
        controller: 'creditPurchasesCtrl'
      })

      .state('purchaseDetails', {
        url: '/page_purchase_details',
        params: {
          username: "",
          token: "",
          credits: "",
          id: ""
        },
        templateUrl: 'templates/purchaseDetails.html',
        controller: 'purchaseDetailsCtrl'
      })

      .state('transactionDetails', {
        url: '/page62',
        params: {
          username: "",
          token: "",
          transaction: ""
        },
        templateUrl: 'templates/transactionDetails.html',
        controller: 'transactionDetailsCtrl'
      })

      .state('paymentConfirmation', {
        url: '/page_payment_confirmation',
        templateUrl: 'templates/paymentConfirmation.html',
        controller: 'paymentConfirmationCtrl'
      })

      .state('menu', {
        url: '/menu',
        templateUrl: 'templates/menu.html',
        controller: 'menuCtrl'
      })

      .state('login', {
        url: '/page_login',
        templateUrl: 'templates/login.html',
        controller: 'loginCtrl'
      })

      .state('signup', {
        url: '/page_signup',
        templateUrl: 'templates/signup.html',
        controller: 'signupCtrl'
      })

      .state('recover', {
        url: '/page_recover',
        templateUrl: 'templates/recover.html',
        controller: 'recoverCtrl'
      })

      .state('resetPassword', {
        url: '/page_reset_password',
        params: {
          username: ""
        },
        templateUrl: 'templates/resetPassword.html',
        controller: 'resetPasswordCtrl'
      })

      .state('changePassword', {
        url: '/page_change_password',
        params: {
          username: "",
          token: ""
        },
        templateUrl: 'templates/changePassword.html',
        controller: 'changePasswordCtrl'
      })

      .state('confirmRegistration', {
        url: '/page_confirm_registration',
        params: {
          username: ""
        },
        templateUrl: 'templates/confirmRegistration.html',
        controller: 'confirmRegistrationCtrl'
      })

      .state('confirmMFA', {
        url: '/page_confirm_mfa',
        params: {
          username: ""
        },
        templateUrl: 'templates/confirmMFA.html',
        controller: 'confirmMFACtrl'
      })

      .state('confirmPhoneNumber', {
        url: '/page_confirm_phone_number',
        params: {
          username: "",
          token: ""
        },
        templateUrl: 'templates/confirmPhoneNumber.html',
        controller: 'confirmPhoneNumberCtrl'
      })

      .state('menu.about', {
        url: '/page_about',
        params: {
          username: "",
          token: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/about.html',
            controller: 'aboutCtrl'
          }
        }
      })

      .state('menu.feedback', {
        url: '/page_feedback',
        params: {
          username: "",
          token: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/feedback.html',
            controller: 'feedbackCtrl'
          }
        }
      })

      .state('addGateway', {
        url: '/page_register_gateway',
        params: {
          username: "",
          token: ""
        },
        templateUrl: 'templates/addGateway.html',
        controller: 'addGatewayCtrl'
      })

      .state('addGatewayGroup', {
        url: '/page_add_gatewatgroup',
        params: {
          username: "",
          token: ""
        },
        templateUrl: 'templates/addGatewayGroup.html',
        controller: 'addGatewayGroupCtrl'
      })

      .state('viewGateway', {
        url: '/page_view_gateway',
        params: {
          username: "",
          token: "",
          devicename: "",
          deviceid: "",
          serialnumber: "",
          timestamp: "",
          heartbeat: "",
          version: "",
          poemacaddress: ""
        },
        templateUrl: 'templates/viewGateway.html',
        controller: 'viewGatewayCtrl'
      })

      .state('updateGatewayGroup', {
        url: '/page_device_group',
        params: {
          username: "",
          token: "",
          devicegroupname: ""
        },
        templateUrl: 'templates/updateGatewayGroup.html',
        controller: 'updateGatewayGroupCtrl'
      })

      .state('viewGatewayGroup', {
        url: '/page_view_gateway_group',
        params: {
          username: "",
          token: "",
          activeSection: "1",
          devicegroupname: ""
        },
        templateUrl: 'templates/viewGatewayGroup.html',
        controller: 'viewGatewayGroupCtrl'
      })

      .state('gatewayLocation', {
        url: '/page_view_gateway_location',
        params: {
          username: "",
          token: "",
          devicename: "",
          deviceid: "",
          serialnumber: "",
          devicestatus: "",
          deviceversion: "",
          location: ""
        },
        templateUrl: 'templates/gatewayLocation.html',
        controller: 'gatewayLocationCtrl'
      })

      .state('oTAFirmwareUpdate', {
        url: '/page_upgrade_device_firmware',
        params: {
          username: "",
          token: "",
          devicename: "",
          deviceid: "",
          serialnumber: "",
          timestamp: "",
          heartbeat: "",
          version: "",
          firmware: ""
        },
        templateUrl: 'templates/oTAFirmwareUpdate.html',
        controller: 'oTAFirmwareUpdateCtrl'
      })

      .state('gatewayGeneralSettings', {
        url: '/page_device_general_settings',
        params: {
          username: "",
          token: "",
          devicename: "",
          deviceid: "",
          serialnumber: "",
          timestamp: "",
          heartbeat: "",
          version: ""
        },
        templateUrl: 'templates/gatewayGeneralSettings.html',
        controller: 'gatewayGeneralSettingsCtrl'
      })

      .state('gatewayDescriptor', {
        url: '/page_gateway_descriptor',
        params: {
          username: "",
          token: "",
          devicename: "",
          deviceid: "",
          serialnumber: "",
          timestamp: "",
          heartbeat: "",
          version: ""
        },
        templateUrl: 'templates/gatewayDescriptor.html',
        controller: 'gatewayDescriptorCtrl'
      })

      .state('gateway', {
        url: '/page_gateway',
        params: {
          devicename: "",
          username: "",
          token: "",
          deviceid: "",
          serialnumber: "",
          deviceversion: "",
          devicestatus: "",
          location: "",
          poemacaddress: ""
        },
        templateUrl: 'templates/gateway.html',
        controller: 'gatewayCtrl'
      })

      .state('menu.sensorDashboard', {
        url: '/page_sensor_dashboard',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/sensorDashboard.html',
            controller: 'sensorDashboardCtrl'
          }
        }
      })

      .state('deviceGPIO', {
        url: '/page_device_gpio',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        templateUrl: 'templates/deviceGPIO.html',
        controller: 'deviceGPIOCtrl'
      })

      .state('deviceUART', {
        url: '/page_device_uart',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        templateUrl: 'templates/deviceUART.html',
        controller: 'deviceUARTCtrl'
      })

      .state('deviceI2C', {
        url: '/page_device_i2c',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        templateUrl: 'templates/deviceI2C.html',
        controller: 'deviceI2CCtrl'
      })

      .state('deviceLDSBUS', {
        url: '/page_ldsbus',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: "",
          activeSection: ""
        },
        templateUrl: 'templates/deviceLDSBUS.html',
        controller: 'deviceLDSBUSCtrl'
      })

      .state('lDSUs', {
        url: '/page_ldsus',
        params: {
          username: "",
          token: "",
          devicename: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: "",
          activeSection: "",
          ldsus: ""
        },
        templateUrl: 'templates/lDSUs.html',
        controller: 'lDSUsCtrl'
      })

      .state('sensors', {
        url: '/page_sensors',
        params: {
          username: "",
          token: "",
          devicename: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: "",
          activeSection: "",
          sensors: ""
        },
        templateUrl: 'templates/sensors.html',
        controller: 'sensorsCtrl'
      })

      .state('actuators', {
        url: '/page_actuators',
        params: {
          username: "",
          token: "",
          devicename: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: "",
          activeSection: "",
          actuators: ""
        },
        templateUrl: 'templates/actuators.html',
        controller: 'actuatorsCtrl'
      })

      .state('deviceADC', {
        url: '/page_device_adc',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        templateUrl: 'templates/deviceADC.html',
        controller: 'deviceADCCtrl'
      })

      .state('deviceTPROBE', {
        url: '/page_device_tprobe',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        templateUrl: 'templates/deviceTPROBE.html',
        controller: 'deviceTPROBECtrl'
      })

      .state('device1WIRE', {
        url: '/page47',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          location: ""
        },
        templateUrl: 'templates/device1WIRE.html',
        controller: 'device1WIRECtrl'
      })

      .state('viewI2CDevice', {
        url: '/page_view_i2c_device',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          attributes: "",
          source: ""
        },
        templateUrl: 'templates/viewI2CDevice.html',
        controller: 'viewI2CDeviceCtrl'
      })

      .state('viewADCDevice', {
        url: '/page_view_adc_device',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          attributes: "",
          source: ""
        },
        templateUrl: 'templates/viewADCDevice.html',
        controller: 'viewADCDeviceCtrl'
      })

      .state('viewTPROBEDevice', {
        url: '/page_view_tprobe_device',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          attributes: "",
          source: "",
          multiclass: ""
        },
        templateUrl: 'templates/viewTPROBEDevice.html',
        controller: 'viewTPROBEDeviceCtrl'
      })

      .state('view1WIREDevice', {
        url: '/page46',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          attributes: "",
          source: ""
        },
        templateUrl: 'templates/view1WIREDevice.html',
        controller: 'view1WIREDeviceCtrl'
      })

  .state('viewLDSUDevice', {
    url: '/page_ldsu_device',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		location: "",
		activeSection: "",
		sensors: "",
		sensor: "",
		source: "",
		multiclass: ""
},
    templateUrl: 'templates/viewLDSUDevice.html',
    controller: 'viewLDSUDeviceCtrl'
  })

  .state('unknown', {
    url: '/page_unknown',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		sensor: ""
},
    templateUrl: 'templates/unknown.html',
    controller: 'unknownCtrl'
  })

      .state('multiclass', {
        url: '/page_multiclass',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: "",
          multiclass: ""
        },
        templateUrl: 'templates/multiclass.html',
        controller: 'multiclassCtrl'
      })

      .state('light', {
        url: '/page_light',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          attributes: "",
          source: "",
          from: ""
        },
        templateUrl: 'templates/light.html',
        controller: 'lightCtrl'
      })

      .state('lightRGB', {
        url: '/page_light_RGB',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          attributes: "",
          source: "",
          colortype: ""
        },
        templateUrl: 'templates/lightRGB.html',
        controller: 'lightRGBCtrl'
      })

  .state('temperature', {
    url: '/page_temperature',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		sensor: "",
		source: "",
		multiclass: "",
		location: "",
		activeSection: "",
		sensors: ""
},
    templateUrl: 'templates/temperature.html',
    controller: 'temperatureCtrl'
  })

  .state('humidity', {
    url: '/page_humidity',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		sensor: "",
		source: "",
		multiclass: "",
		location: "",
		activeSection: "",
		sensors: ""
},
    templateUrl: 'templates/humidity.html',
    controller: 'humidityCtrl'
  })

      .state('display', {
        url: '/page_display',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: ""
        },
        templateUrl: 'templates/display.html',
        controller: 'displayCtrl'
      })

      .state('speaker', {
        url: '/page_speaker',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: ""
        },
        templateUrl: 'templates/speaker.html',
        controller: 'speakerCtrl'
      })

      .state('potentiometer', {
        url: '/page_potentiometer',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: ""
        },
        templateUrl: 'templates/potentiometer.html',
        controller: 'potentiometerCtrl'
      })

      .state('anemometer', {
        url: '/page_anenometer',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: ""
        },
        templateUrl: 'templates/anemometer.html',
        controller: 'anemometerCtrl'
      })

      .state('battery', {
        url: '/page_battery',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: ""
        },
        templateUrl: 'templates/battery.html',
        controller: 'batteryCtrl'
      })

      .state('fluid', {
        url: '/page_fluid',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          sensor: "",
          source: ""
        },
        templateUrl: 'templates/fluid.html',
        controller: 'fluidCtrl'
      })

      .state('addI2CDevice', {
        url: '/page_add_i2c_device',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          i2cnumber: ""
        },
        templateUrl: 'templates/addI2CDevice.html',
        controller: 'addI2CDeviceCtrl'
      })

      .state('addADCDevice', {
        url: '/page_add_adc_device',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          adcnumber: ""
        },
        templateUrl: 'templates/addADCDevice.html',
        controller: 'addADCDeviceCtrl'
      })

      .state('addTPROBEDevice', {
        url: '/page_add_tprobe_device',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          tprobenumber: ""
        },
        templateUrl: 'templates/addTPROBEDevice.html',
        controller: 'addTPROBEDeviceCtrl'
      })

      .state('add1WIREDevice', {
        url: '/page45',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          onewirenumber: ""
        },
        templateUrl: 'templates/add1WIREDevice.html',
        controller: 'add1WIREDeviceCtrl'
      })

      .state('addI2CDeviceDetails', {
        url: '/page_add_i2c_device_details',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          i2c: "",
          i2cnumber: ""
        },
        templateUrl: 'templates/addI2CDeviceDetails.html',
        controller: 'addI2CDeviceDetailsCtrl'
      })

      .state('addADCDeviceDetails', {
        url: '/page_add_adc_device_details',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          adc: "",
          adcnumber: ""
        },
        templateUrl: 'templates/addADCDeviceDetails.html',
        controller: 'addADCDeviceDetailsCtrl'
      })

      .state('addTPROBEDeviceDetails', {
        url: '/page16',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          tprobe: "",
          tprobenumber: ""
        },
        templateUrl: 'templates/addTPROBEDeviceDetails.html',
        controller: 'addTPROBEDeviceDetailsCtrl'
      })

      .state('add1WIREDeviceDetails', {
        url: '/page43',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          onewire: "",
          onewirenumber: ""
        },
        templateUrl: 'templates/add1WIREDeviceDetails.html',
        controller: 'add1WIREDeviceDetailsCtrl'
      })

      .state('deviceNotifications', {
        url: '/page_device_notifications',
        params: {
          devicename: "",
          username: "",
          token: "",
          devicestatus: "",
          deviceid: "",
          serialnumber: "",
          status: ""
        },
        templateUrl: 'templates/deviceNotifications.html',
        controller: 'deviceNotificationsCtrl'
      })

      .state('menu.troubleshooting', {
        url: '/page_troubleshooting',
        params: {
          username: "",
          token: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/troubleshooting.html',
            controller: 'troubleshootingCtrl'
          }
        }
      })

      .state('menu.alerts', {
        url: '/page_alerts',
        params: {
          username: "",
          token: ""
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/alerts.html',
            controller: 'alertsCtrl'
          }
        }
      })

      .state('menu.organizations', {
        url: '/page_organizations',
        params: {
          username: "",
          token: "",
          section: "1"
        },
        views: {
          'side-menu21': {
            templateUrl: 'templates/organizations.html',
            controller: 'organizationsCtrl'
          }
        }
      })

      .state('addOrganizationUser', {
        url: '/page_add_organization_user',
        params: {
          username: "",
          token: "",
          orgname: ""
        },
        templateUrl: 'templates/addOrganizationUser.html',
        controller: 'addOrganizationUserCtrl'
      })

      .state('addOrganizationGroup', {
        url: '/page_add_organization_group',
        params: {
          username: "",
          token: "",
          orgname: ""
        },
        templateUrl: 'templates/addOrganizationGroup.html',
        controller: 'addOrganizationGroupCtrl'
      })

      .state('addOrganizationPolicy', {
        url: '/page_add_organization_policy',
        params: {
          username: "",
          token: "",
          orgname: ""
        },
        templateUrl: 'templates/addOrganizationPolicy.html',
        controller: 'addOrganizationPolicyCtrl'
      })

      .state('updateOrganizationPolicy', {
        url: '/page_update_organization_policy',
        params: {
          username: "",
          token: "",
          orgname: "",
          policyname: "",
          settings: "",
          type: ""
        },
        templateUrl: 'templates/updateOrganizationPolicy.html',
        controller: 'updateOrganizationPolicyCtrl'
      })

      .state('updateOrganizations', {
        url: '/page_create_organization',
        params: {
          username: "",
          token: ""
        },
        templateUrl: 'templates/updateOrganizations.html',
        controller: 'updateOrganizationsCtrl'
      })

      .state('updateOrganizationGroupUsers', {
        url: '/page_update_organization_group_users',
        params: {
          username: "",
          token: "",
          orgname: "",
          groupname: ""
        },
        templateUrl: 'templates/updateOrganizationGroupUsers.html',
        controller: 'updateOrganizationGroupUsersCtrl'
      })

      .state('updateOrganizationGroupPolicies', {
        url: '/page_update_organization_group_policies',
        params: {
          username: "",
          token: "",
          orgname: "",
          groupname: ""
        },
        templateUrl: 'templates/updateOrganizationGroupPolicies.html',
        controller: 'updateOrganizationGroupPoliciesCtrl'
      })

    $urlRouterProvider.otherwise('/page_home')


  });
