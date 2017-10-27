angular.module('app').controller('logoutCtrl', ['$scope', '$location', 'AuthService', '$cookies',
  function($scope, $location, AuthService, $cookies) {
    $scope.logout = function() {
      console.log(AuthService.isLoggedInCheck());
      // call logout from service
      AuthService.logout()
        .then(function() {
          //$cookies.put('usr','');
          //  $cookies.put('isLoggedIn', false);
          $location.path('/login');
        });
    };
  }
]);
