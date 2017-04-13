angular.module('App', [])
	.controller('homeController', function($scope, $http) {
		$scope.results = []
		$scope.summary="Here goes the summary"
		$scope.processQuery = function() {
	  		console.log($scope.query)
			let q = $scope.query
			let url = "https://api.cognitive.microsoft.com/bing/v5.0/search?count=15&q=" + q
			$http({
				method: 'GET',
				url: url,
				headers: {
					'Ocp-Apim-Subscription-Key': '3b8a262458034bc897cb331d12b5609f'
				}
			}).then((data)=>{
				$scope.results = data.data.webPages.value
				console.log($scope.results)
				//TODO make a post to your server with the required data. process and recieve it to $scope.summary
				$scope.summary = "summary about "+q
			});
			$scope.query = '';
		};
 	});
