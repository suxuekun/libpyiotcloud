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

  .state('configureDevice', {
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
    templateUrl: 'templates/configureDevice.html',
    controller: 'configureDeviceCtrl'
  })

  .state('deviceEthernet', {
    url: '/page_device_ethernet',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: ""		
},
    templateUrl: 'templates/deviceEthernet.html',
    controller: 'deviceEthernetCtrl'
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

  .state('viewI2CDevice', {
    url: '/page_view_i2c_device',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		sensor: ""		
},
    templateUrl: 'templates/viewI2CDevice.html',
    controller: 'viewI2CDeviceCtrl'
  })

  .state('light', {
    url: '/page33',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: "",
		sensor: ""		
},
    templateUrl: 'templates/light.html',
    controller: 'lightCtrl'
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
		sensor: ""		
},
    templateUrl: 'templates/temperature.html',
    controller: 'temperatureCtrl'
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
		sensor: ""		
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
		sensor: ""		
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
		sensor: ""		
},
    templateUrl: 'templates/potentiometer.html',
    controller: 'potentiometerCtrl'
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

  .state('deviceNotifications', {
    url: '/page_device_notifications',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: "",
		deviceid: "",
		serialnumber: ""		
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

$urlRouterProvider.otherwise('/page_home')


});