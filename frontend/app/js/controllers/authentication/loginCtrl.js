angular.module('app').controller('loginCtrl', ['$scope', '$location', 'AuthService', '$cookies', 'SharedProperties', 'GlobalFcnService',
  function($scope, $location, AuthService, $cookies, SharedProperties, GlobalFcnService) {
    //console.log(AuthService.isLoggedInCheck());
    //$scope.errorMessage="error message";
    $scope.hasData = true;

    function setCookie(cname, cvalue, exdays) {
      var d = new Date();
      d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
      var expires = "expires=" + d.toUTCString();
      document.cookie = cname + "=" + cvalue + "; " + expires;
    }

    $scope.init = function() {
      // $scope.loginForm1 = {};
    };

    $scope.goToLocation = function(path) {
      $location.path(path);
    };

    $scope.login = function() {
      // initial values
      $scope.error = false;
      $scope.disabled = true;
      console.log($scope.loginForm1);

      if ($scope.loginForm1.username.$modelValue === undefined || $scope.loginForm1.password.$modelValue === undefined) {
        alert("Fill in the required fields");
        return;
      }

      $scope.hasData = false;
      // call login from service
      AuthService.login($scope.loginForm1.username.$modelValue, $scope.loginForm1.password.$modelValue)
        // handle success
        .then(function(data) {
          console.log("AuthService.login ok");
          $scope.hasData = true;
          // console.log(data);

          /*  var username = GetCookie("username");

            if ((!username) || (username == 'null'))

            {
              username = prompt("Please enter your name:", "");
            }*/

          setCookie("username", $scope.loginForm1.username.$modelValue, new Date());

          // request user settings and save into SharedProperties

          GlobalFcnService.requestAndSaveAppSettings();

          $location.path('/home');
          $scope.disabled = false;
          $scope.loginForm1 = {};
          //$cookies.put('usr',$scope.loginForm.username);
          //$cookies.put('isLoggedIn', true);
        })
        // handle error
        .catch(function(error) {
          $scope.error = true;
          console.log(error);
          $scope.disabled = false;
          $scope.newUser.username = undefined;
          $scope.newUser.password = undefined;
          $scope.hasData = true;
          alert("The login information you entered does not match an existing account");

          //$cookies.put('usr','');
          //$cookies.put('isLoggedIn', false);
        });

    };

  }
]);
