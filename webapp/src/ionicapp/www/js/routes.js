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

  .state('confirmRegistration', {
    url: '/page_confirm_registration',
	params: {
		username: ""		
},
    templateUrl: 'templates/confirmRegistration.html',
    controller: 'confirmRegistrationCtrl'
  })

  .state('menu.help', {
    url: '/page_help',
    views: {
      'side-menu21': {
        templateUrl: 'templates/help.html',
        controller: 'helpCtrl'
      }
    }
  })

  .state('menu.settings', {
    url: '/page_settings',
    views: {
      'side-menu21': {
        templateUrl: 'templates/settings.html',
        controller: 'settingsCtrl'
      }
    }
  })

  .state('registerDevice', {
    url: '/page_register_device',
	params: {
		username: "",
		token: ""		
},
    templateUrl: 'templates/registerDevice.html',
    controller: 'registerDeviceCtrl'
  })

  .state('viewDevice', {
    url: '/page_view_device',
	params: {
		username: "",
		token: "",
		devicename: "",
		deviceid: "",
		devicecert: "",
		devicepkey: "",
		deviceca: ""		
},
    templateUrl: 'templates/viewDevice.html',
    controller: 'viewDeviceCtrl'
  })

  .state('controlDevice', {
    url: '/page_control_device',
	params: {
		devicename: "",
		username: "",
		token: ""		
},
    templateUrl: 'templates/controlDevice.html',
    controller: 'controlDeviceCtrl'
  })

  .state('deviceEthernet', {
    url: '/page_device_ethernet',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: ""		
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
		devicestatus: ""		
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
		devicestatus: ""		
},
    templateUrl: 'templates/deviceUART.html',
    controller: 'deviceUARTCtrl'
  })

  .state('deviceRTC', {
    url: '/page_device_rtc',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: ""		
},
    templateUrl: 'templates/deviceRTC.html',
    controller: 'deviceRTCCtrl'
  })

  .state('deviceNotifications', {
    url: '/page_device_notifications',
	params: {
		devicename: "",
		username: "",
		token: "",
		devicestatus: ""		
},
    templateUrl: 'templates/deviceNotifications.html',
    controller: 'deviceNotificationsCtrl'
  })

  .state('menu.history', {
    url: '/page_history',
    views: {
      'side-menu21': {
        templateUrl: 'templates/history.html',
        controller: 'historyCtrl'
      }
    }
  })

$urlRouterProvider.otherwise('/page_home')


});