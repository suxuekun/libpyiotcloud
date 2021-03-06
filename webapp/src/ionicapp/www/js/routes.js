angular.module('app.routes', [])

.config(function($stateProvider, $urlRouterProvider) {

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

  .state('menu.devices', {
    url: '/page_devices',
	params: {
		username: "",
		token: ""		
},
    views: {
      'side-menu21': {
        templateUrl: 'templates/devices.html',
        controller: 'devicesCtrl'
      }
    }
  })

  .state('menu.account', {
    url: '/page_account',
	params: {
		username: "",
		token: ""		
},
    views: {
      'side-menu21': {
        templateUrl: 'templates/account.html',
        controller: 'accountCtrl'
      }
    }
  })

  .state('order', {
    url: '/page_order',
	params: {
		username: "",
		token: ""		
},
    templateUrl: 'templates/order.html',
    controller: 'orderCtrl'
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

  .state('menu.helpSupport', {
    url: '/page_help',
	params: {
		username: "",
		token: ""		
},
    views: {
      'side-menu21': {
        templateUrl: 'templates/helpSupport.html',
        controller: 'helpSupportCtrl'
      }
    }
  })

  .state('addDevice', {
    url: '/page_register_device',
	params: {
		username: "",
		token: ""		
},
    templateUrl: 'templates/addDevice.html',
    controller: 'addDeviceCtrl'
  })

  .state('viewDevice', {
    url: '/page_view_device',
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
    templateUrl: 'templates/viewDevice.html',
    controller: 'viewDeviceCtrl'
  })

  .state('deviceGeneralSettings', {
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
    templateUrl: 'templates/deviceGeneralSettings.html',
    controller: 'deviceGeneralSettingsCtrl'
  })

  .state('device', {
    url: '/page_control_device',
	params: {
		devicename: "",
		username: "",
		token: "",
		deviceid: "",
		serialnumber: "",
		deviceversion: "",
		devicestatus: ""		
},
    templateUrl: 'templates/device.html',
    controller: 'deviceCtrl'
  })

  .state('sensorDashboard', {
    url: '/page_sensor_dashboard',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: ""		
},
    templateUrl: 'templates/sensorDashboard.html',
    controller: 'sensorDashboardCtrl'
  })

  .state('sensorChart', {
    url: '/page_sensor_chart',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		sensor: ""		
},
    templateUrl: 'templates/sensorChart.html',
    controller: 'sensorChartCtrl'
  })

  .state('deviceGPIO', {
    url: '/page_device_gpio',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: ""		
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
		serialnumber: ""		
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
		serialnumber: ""		
},
    templateUrl: 'templates/deviceI2C.html',
    controller: 'deviceI2CCtrl'
  })

  .state('deviceADC', {
    url: '/page_device_adc',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: ""		
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
		serialnumber: ""		
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
		serialnumber: ""		
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
		multiclass: ""		
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
		multiclass: ""		
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

  .state('menu.history', {
    url: '/page_history',
	params: {
		username: "",
		token: ""		
},
    views: {
      'side-menu21': {
        templateUrl: 'templates/history.html',
        controller: 'historyCtrl'
      }
    }
  })

  .state('menu.notification', {
    url: '/page_notification',
	params: {
		username: "",
		token: ""		
},
    views: {
      'side-menu21': {
        templateUrl: 'templates/notification.html',
        controller: 'notificationCtrl'
      }
    }
  })

$urlRouterProvider.otherwise('/page_login')


});