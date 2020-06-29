;(function(_global){
	app = _global.app

	// function getHeader(User){
	// 	return {'Authorization': 'Bearer ' + User.get_token().access}
	// }
	
	app
	.controller('transactionCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token','BraintreePayment', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
	// You can include any angular dependencies as parameters for this function
	// TIP: Access Route Parameters for your page via $stateParams.parameterName
		function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token, BraintreePayment) {
		    $scope.data ={}
		    $scope.start = function(){
		    	BraintreePayment.get_transactions()
		    	.then(function(res){
		    		$scope.data.transactions = res.data.data
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    	
		    }
		    $scope.clean = function(){

		    }
			$scope.$on('$ionicView.enter', function(e) {
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });
		}
	])
	.controller('billingAddressCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token','BraintreePayment', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
	// You can include any angular dependencies as parameters for this function
	// TIP: Access Route Parameters for your page via $stateParams.parameterName
		function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token, BraintreePayment) {
		    $scope.data ={}
		    $scope.start = function(){
		    	BraintreePayment.get_billing_address()
		    	.then(function(res){
		    		$scope.data = res.data.data
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    }
		    $scope.update_address = function(){
		    	BraintreePayment.save_billing_address($scope.data)
		    	.then(function(res){
		    		$ionicPopup.alert({ title: 'Success', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    }
		    $scope.clean = function(){

		    }
		    $scope.viewSubscription = function(subscription){
		    	$state.go('menu.subscription_detail',{'subscription':subscription})
		    }
			$scope.$on('$ionicView.enter', function(e) {
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });
		}
	])
	.controller('subscriptionCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token','BraintreePayment', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
	// You can include any angular dependencies as parameters for this function
	// TIP: Access Route Parameters for your page via $stateParams.parameterName
		function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token, BraintreePayment) {
		    $scope.data ={}
		    $scope.start = function(){
		    	BraintreePayment.get_subscriptions()
		    	.then(function(res){
		    		$scope.data.subscriptions = res.data.data
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    	
		    }
		    $scope.clean = function(){

		    }
		    $scope.viewSubscription = function(subscription){
		    	$state.go('menu.subscription_detail',{'subscription':subscription})
		    }
			$scope.$on('$ionicView.enter', function(e) {
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });
		}
	])
	.controller('subscriptionDetailCtrl',['$scope','$http','BraintreePayment','User','$ionicPopup','$stateParams','$state',
		function($scope,$http,BraintreePayment,User,$ionicPopup,$stateParams,$state){
			$scope.data = {}
			$scope.start = function(){
				$scope.data = $stateParams
				
		    }
		    $scope.clean = function(){

		    }
		    $scope.upgrade = function(){
		    	$scope.data.ui = {
		    		title :'Upgrade Plan',
		    		name :'Upgrade',
		    	}
		    	$state.go('menu.subscription_change',$scope.data)
		    }
		    $scope.cancel = function(){
		    	BraintreePayment.cancel_subscription({subscription_id:$scope.data.subscription._id})
		    	.then(function(res){
		    		$scope.data.subscription.status = 'cancel'
		    	})

		    }
		    $scope.back = function(){
		    	$state.go('menu.subscription')
		    }
			$scope.$on('$ionicView.enter', function(e) {
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });

		}])
	.controller('subscriptionChangeCtrl',['$scope','$http','BraintreePayment','User','$ionicPopup','$stateParams','$state',
		function($scope,$http,BraintreePayment,User,$ionicPopup,$stateParams,$state){
			
			$scope.data = {}
			
			$scope.start = function(){
				$scope.data = $stateParams
				BraintreePayment.get_plans()
		    	.then(function(res){
		    		$scope.data.plans = res.data.data
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    }
		    $scope.clean = function(){

		    }
		    $scope.choosePlan = function(plan){
		    	console.log(plan)
		    	$scope.data.plans.forEach(function(item){
		    		
		    		item.choose = false
		    	})
		    	plan.choose = true
		    	$scope.data.plan = plan
		    }
		    $scope.changePlan = function(){
		    	console.log('change plan')
		    	$state.go('menu.subscription_change_confirm',$scope.data)
		    }
		    $scope.back = function(){
		    	$state.go('menu.subscription_detail',$scope.data)
		    }
			$scope.$on('$ionicView.enter', function(e) {
				
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });

		}])
	.controller('subscriptionConfirmChangeCtrl',['$scope','$http','BraintreePayment','User','$ionicPopup','$stateParams','$state',
		function($scope,$http,BraintreePayment,User,$ionicPopup,$stateParams,$state){
			
			$scope.data = {}
			
			$scope.start = function(){
				console.log('enter confirm page')
				$scope.data = $stateParams
				// console.log($scope.data,$stateParams)
				$scope.calc_prorate()

		    }
		    $scope.get_use_plan_name = function(){
		    	var pre_sub = $scope.get_use_plan()
		    	if (!pre_sub) return ""
		    	return pre_sub.plan.name
		    }
		    $scope.get_use_plan = function(){
		    	if(!$scope.data.subscription) return
		    	var pre_sub = $scope.data.subscription.current
		    	return pre_sub
		    }

		    $scope.calc_prorate = function(){
		    	var pre_sub = $scope.get_use_plan()
		    	if (!pre_sub){
		    		return 
		    	}
		    	var old_id = pre_sub.plan._id
				var new_id = $scope.data.plan._id
				var promocode = null
				if ($scope.data.promocode){
					promocode = $scope.data.promocode.code
				}
				BraintreePayment.prorate(old_id,new_id,promocode)
				.then(function(res){
					$scope.data.prorate = res.data.data
				})
		    }
		    $scope.clean = function(){

		    }
		  
		    $scope.applyCode = function(){
		    	$state.go('menu.subscription_promocode',$scope.data)
		    }
		    $scope.removeCode = function(){
		    	$scope.data.promocode = null
		    }

		    $scope.back = function(){
		    	$state.go('menu.subscription_change',$scope.data)
		    }
			$scope.$on('$ionicView.enter', function(e) {
				console.log('wtf enter')
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });

			$scope.pay = function(){
				$state.go('menu.subscription_payment',$scope.data)
			}
			

		}])
	.controller('subscriptionPaymentCtrl',['$scope','$http','BraintreePayment','User','$ionicPopup','$stateParams','$state',
		function($scope,$http,BraintreePayment,User,$ionicPopup,$stateParams,$state){
			
			$scope.data = {}
			
			$scope.start = function(){
				console.log('enter confirm page')
				$scope.data = $stateParams
				// console.log($scope.data,$stateParams)

				BraintreePayment.get_client_token().then(function(res){
					console.log('get token',$scope.token)
					$scope.token = res.data.data
					braintree.dropin.create({
						authorization: $scope.token,
						container: '#dropin-container',
						// threeDSecure:true,
						paypal: {
							flow: 'vault'
						}
					}, function (createErr, instance) {
						console.log('rebuild instance',instance,createErr)
						if (instance){
							$scope.ready = true
							$scope.instance = instance
							console.log('ready')
							$scope.$apply()
						}
					})
				})
		    }
		    
		    $scope.clean = function(){
		    	$scope.instance.teardown(function (teardownErr) {
				  if (teardownErr) {
				    console.error('Could not tear down Drop-in UI!');
				  } else {
				    console.info('Drop-in UI has been torn down!');
				  }
				});
		    }
		    $scope.back = function(){
		    	$state.go('menu.subscription_change_confirm',$scope.data)
		    }
			$scope.$on('$ionicView.enter', function(e) {
				console.log('wtf enter')
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });

			$scope.pay = function(){
				$scope.instance.requestPaymentMethod(function (err, payload) {
					console.log(err,"NONCE: " + payload.nonce);
					$scope.executePay(payload.nonce)
//					FinalizePayment(plan, payload.nonce, payload.details, payload.type)
				});
			}
			$scope.executePay = function(nonce){
				
				var one_change = {
						subscription_id:$scope.data.subscription._id,
						plan_id:$scope.data.plan._id,
					}

				if ($scope.data.promocode){
					one_change.promocode = $scope.data.promocode.code
				}
				var data = {
					items:[one_change],
					nonce:nonce,
				}
				console.log(data)
				BraintreePayment.checkout(data).then(function(res){
					alert(res.data.message)
				},function(res){
					alert(res.data.message)
				})
			}

		}])
	.controller('subscriptionPromocodeCtrl',['$scope','$http','BraintreePayment','User','$ionicPopup','$stateParams','$state',
		function($scope,$http,BraintreePayment,User,$ionicPopup,$stateParams,$state){
			
			$scope.data = {}
			$scope.start = function(){
				$scope.data = $stateParams
				BraintreePayment.get_promocodes()
		    	.then(function(res){
		    		$scope.data.promocodes = res.data.data
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    }
		    $scope.clean = function(){

		    }
		    $scope.verifyCode = function(code){
		    	BraintreePayment.verify_promocode(code)
		    	.then(function(res){
		    		promocode = res.data.data
		    		$scope.chooseCode(promocode)
		    	},function(res){
					$ionicPopup.alert({ title: 'Error', template: res.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
		    	})
		    	
		    }
		    $scope.chooseCode = function(promocode){
		    	$scope.data.promocode = promocode
		    	$scope.back()
		    }
		    $scope.back = function(){
		    	console.log($scope.data)
		    	$state.go('menu.subscription_change_confirm',$scope.data)
		    }
			$scope.$on('$ionicView.enter', function(e) {
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });

		}])

}(window))