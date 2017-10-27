angular.module('app').controller('settingsWeatherCtrl', ['SharedProperties', 'GlobalFcnService', '$scope', '$timeout',
  '$log', '$http',
  function(SharedProperties, GlobalFcnService, $scope, $timeout, $log, $http) {

    $scope.hasData = true;
    $scope.weatherRequests = [{
      'id': 0,
      'name': 'forecast',
      'url': 'http://api.openweathermap.org/data/2.5/forecast/daily'
    }, {
      'id': 1,
      'name': 'current',
      'url': 'http://api.openweathermap.org/data/2.5/weather'
    }];

    $scope.locations = [{
      'name': 'Bucharest'
    }];


    $scope.init = function() {
      $scope.serverURL = SharedProperties.getProperty().url;
      $scope.selectedReqType = $scope.weatherRequests[1];
      $scope.selectedLocation = $scope.locations[0];
      $scope.weatherRequest = {
        method: 'GET',
        url: $scope.selectedReqType.url,
        params: {
          q: $scope.selectedLocation.name,
          mode: 'json',
          units: 'metric',
          cnt: '7',
          appid: '13d3396479dc92a69c579d67bd4835cc'
        }
      };
      $scope.getSettings();
      //$scope.getData();
    };


    $scope.getSettings = function() {
      var user = GlobalFcnService.getCookie("username");
      console.log(user);

      if ($scope.settings === undefined) {
        $scope.settings = {};
      }
      $scope.hasData = false;
      var promise = $http.get($scope.serverURL + '/api/settings', {
        params: {
          username: user
        }
      }).
      then(function(response) {
        $scope.jsondata = angular.toJson(response.data);
        var jsonObj = angular.fromJson(response.data);
        if (jsonObj !== false) {
          if (jsonObj[0] !== undefined) {
            var uo = jsonObj[0].JsonString;
            var jsonObj2 = angular.fromJson(uo);
            $scope.settings.userOptions = jsonObj2;
            $scope.weatherRequest.params.appid = jsonObj2.appid;
          }
        }
      }, function(err) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        alert('error');
      });

      return promise;
    };

    var updateUserOptions = function() {
      $scope.settings.userOptions.appid = $scope.weatherRequest.params.appid;
    };

    $scope.postSettings = function() {
      updateUserOptions();
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/settings', {
        'username': GlobalFcnService.getCookie("username"),
        'settings': angular.toJson($scope.settings.userOptions)
      }).
      then(function(response) {
        console.log('post success');
      }, function(err) {
        console.log('post error');
        $scope.hasData = true;
        alert('error');
      });

    };

    $scope.getData = function() {
      $scope.weatherRequest.url = $scope.selectedReqType.url;
      $scope.weatherRequest.params.q = $scope.selectedLocation.name;
      $scope.hasWeatherData = false;
      $scope.hasData = false;
      $http($scope.weatherRequest)
        .then(function(response) {
          $scope.weatherData = response.data;
          $scope.hasWeatherData = true;
        }).
      catch(function(response) {
        $scope.hasData = true;
        alert('error');
      });
    };

    $scope.$on('$destroy', function(event) {});

  }
]);
