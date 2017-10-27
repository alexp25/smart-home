angular.module('app').controller('configCtrl', ['SharedProperties', 'StorageService', '$scope', '$log', '$timeout', '$location',
  function(SharedProperties, StorageService, $scope, $log, $timeout, $location) {

    $scope.localStorage = {};
    $scope.updateStorage = function() {

      if ($scope.localStorage.url === undefined) {
        $scope.localStorage.url = '';
      }
      if ($scope.localStorage.wsurl === undefined) {
        $scope.localStorage.wsurl = 'ws://' + document.location.host;
      }


      StorageService.setData($scope.localStorage);


      SharedProperties.setOneProperty('url', $scope.localStorage.url);
      SharedProperties.setOneProperty('wsurl', $scope.localStorage.wsurl);
      $location.path("/");
    };
    $scope.init = function() {
      var data = StorageService.getData();
      console.log("config storage: ", data);
      if (data !== undefined) {
        $scope.localStorage = data;
      }
    };
  }
]);
