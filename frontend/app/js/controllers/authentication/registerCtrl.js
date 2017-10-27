angular.module('app').controller('registerCtrl', ['$scope', '$location', '$http', 'SharedProperties',
  function($scope, $location, $http, SharedProperties) {

    $scope.hasData = true;
    $scope.register = function() {
      $scope.serverURL = SharedProperties.getProperty().url;
      console.log($scope.registerForm1);
      if ($scope.registerForm1.username.$modelValue === undefined|| $scope.registerForm1.email.$modelValue === undefined) {
        alert("Fill in the required fields");
        return;
      }

      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/register',
          $scope.newUser
        )
        // handle success
        .then(function(data) {
          console.log(data);
          $scope.hasData = true;
          if (data.data.result === SharedProperties.getProperty().constants.RESULT_FAIL) {
            alert("error: user already in the database");
          } else if (data.data.result === SharedProperties.getProperty().constants.RESULT_OK) {
            alert("To complete the registration click on the link sent to your email");
            $scope.goToLogin();
          }
        })
        // handle error
        .catch(function(data) {
          $scope.newUser.username=undefined;
          $scope.newUser.email=undefined;
          $scope.hasData=true;
          alert('error');
        });
    };

    $scope.goToLogin = function() {
      $location.path('/login');
    };

  }
]);
