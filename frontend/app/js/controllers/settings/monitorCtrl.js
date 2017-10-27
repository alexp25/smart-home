angular.module('app').controller('settingsMonitorCtrl', ['SharedProperties', 'GlobalFcnService', '$scope', '$timeout',
  '$log', '$http', '$mdSidenav',
  function(SharedProperties, GlobalFcnService, $scope, $timeout, $log, $http, $mdSidenav) {

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

    $scope.settings = {};

    $scope.postSettings = function() {
      console.log($scope.settings.data);
      GlobalFcnService.postSettings({
        "collection": "monitor",
        "data": $scope.settings.data
      });
    };

    $scope.getSettings = function() {
      $scope.hasData = false;
      GlobalFcnService.getSettings().then(function(response) {
        n = response.data;
        $scope.settings.model = n.settingsModel;
        $scope.settings.data = {};
        $scope.settings.data = setData($scope.settings.data, $scope.settings.model, n.userSettings.monitor);
        $scope.hasData = true;
      }, function(err) {
        // handle possible errors that occur when making the request.
        $scope.hasData = true;
        alert('error');
      });
    };

    var setData = function(data, model, settings) {
      var i, j;

      // set default values from model
      for (i = 0; i < model.monitor.length; i++) {
        data[model.monitor[i].name] = model.monitor[i].default;
      }
      // update with actual values from the database
      angular.forEach(settings, function(value, key) {
        // this.push(key + ': ' + value);
        if (data[key] !== undefined) {
          data[key] = value;
        }
      });
      return data;
    };


    $scope.init = function() {
      $scope.getSettings();
    };


    $scope.$on('$destroy', function(event) {});
  }
]);
