angular.module('app').controller('settingsUserCtrl', ['$scope', '$timeout',
  '$log', '$http', 'SharedProperties', 'GlobalFcnService',
  function($scope, $timeout, $log, $http, SharedProperties, GlobalFcnService) {

    $scope.init = function() {
      $scope.serverURL = SharedProperties.getProperty().url;
      $scope.getUserInfo();
    };


    $scope.getUserInfo = function() {
      $scope.hasData = false;
      var user = GlobalFcnService.getCookie("username");
      console.log(user);
      $http.get($scope.serverURL + '/api/database/user-info', {
        params: {
          username: user
        }
      }).
      then(function(response) {
        $scope.jsonObj = angular.fromJson(response.data);
        $scope.userInfo = response.data;
        console.log($scope.jsonObj);
        $scope.hasData = true;
      }, function(err) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        alert('error');
      });
    };

    $scope.updateUserInfo = function() {
      $scope.hasData = false;
      var user = GlobalFcnService.getCookie("username");
      console.log(user);
      $http.post($scope.serverURL + '/api/database/user-info', $scope.userInfo).
      then(function(response) {
        var js = angular.fromJson(response.data);
        if (js.result === SharedProperties.getProperty().constants.RESULT_FAIL) {
          $scope.hasData = true;
          alert('error');
        } else {
          $scope.hasData = true;
        }
      }, function(err) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        alert('error');
      });
    };

  }
]);
