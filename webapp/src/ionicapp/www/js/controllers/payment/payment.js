;(function(_global){
	app = _global.app

	// function getHeader(User){
	// 	return {'Authorization': 'Bearer ' + User.get_token().access}
	// }
	
	app
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
				console.log($scope.data)
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
			console.log($scope.data)
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
				console.log('wtf enter')
				$scope.start()
		    });
		    $scope.$on('$ionicView.beforeLeave', function(e) {
		    	$scope.clean()
		    });

		}])
	.controller('subscriptionConfirmChangeCtrl',['$scope','$http','BraintreePayment','User','$ionicPopup','$stateParams','$state',
		function($scope,$http,BraintreePayment,User,$ionicPopup,$stateParams,$state){
			
			$scope.data = {}
			$scope.paymentParam = {}
			console.log($scope.data)
			$scope.start = function(){
				$scope.data = $stateParams
				BraintreePayment.get_client_token().then(function(res){
					$scope.token = res.data.data
					braintree.dropin.create({
						authorization: $scope.token,
						container: '#dropin-container',
						// threeDSecure:true,
						paypal: {
							flow: 'vault'
						}
					}, function (createErr, instance) {
						
						if (instance){
							$scope.ready = true
							$scope.instance = instance
							console.log('ready')
							$scope.$apply()
						}
					})
				})
				BraintreePayment.get_promocodes().then(function(res){
					$scope.data.promocodes = res.data.data
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
				$scope.instance.requestPaymentMethod(function (err, payload) {
					console.log("NONCE: " + payload.nonce);
					$scope.executePay(payload.nonce)
//					FinalizePayment(plan, payload.nonce, payload.details, payload.type)
				});
			}
			$scope.executePay = function(nonce){
				var data = {
					changes:[{
						subscription:$scope.data.subscriptio._id,
						plan:$scope.data.plan._id
					}],
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

}(window))