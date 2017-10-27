angular.module('app').controller('settingsAdminCtrl', ['$scope', '$timeout',
  '$log', '$http', 'SharedProperties',
  function($scope, $timeout, $log, $http, SharedProperties) {
    $scope.users = [];
    $scope.user = {
      deleteOlderThan: 30,
      new: {
        name: '',
        password: ''
      },
      name: undefined
    };

    $scope.init = function() {
      //$scope.getTableNames();
      var props = SharedProperties.getProperty();
      $scope.serverURL = props.url;
      $scope.getUserNames();
    };

    $scope.getUserNames = function() {
      $scope.error = false;
      $scope.hasData = false;
      $http.get($scope.serverURL + '/api/database/users').
      then(function(data) {
        $scope.jsonObj = angular.fromJson(data.data);
        $scope.users = $scope.jsonObj;
        console.log($scope.jsonObj);
        $scope.selectedUser = $scope.users[0];
        $scope.hasData = true;
      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        alert('error');
      });
    };

    $scope.deleteUser = function(username) {
      $scope.error = false;
      if (username === '' || username === undefined) {
        $scope.error = true;
        $scope.errorMessage = 'Select username from list';
        return;
      }
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/database/users', {
        'req': 2,
        'username': username
      }).
      then(function(data) {
        $scope.hasData = true;
        console.log('post success');
        if (data.data.result === SharedProperties.getProperty().constants.RESULT_FAIL) {
          alert("Removing the only user is not permitted");
        }
      }).
      catch(function(data) {
        console.log('post error');
        $scope.hasData = true;
        alert('error');
      });
    };

    $scope.deleteOlderThan = function(value) {
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/database/sensors/delete', {
        'type': 1,
        'value': value
      }).
      then(function(data) {
        $scope.hasData = true;
        console.log('post success');
      }).
      catch(function(data) {
        console.log('post error');
        $scope.hasData = true;
        alert('error');
      });
    };

  }
]);
