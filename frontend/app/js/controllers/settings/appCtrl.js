angular.module('app').controller('settingsAppCtrl', ['SharedProperties', 'GlobalFcnService', '$scope', '$timeout',
  '$log', '$http', '$mdSidenav',
  function(SharedProperties, GlobalFcnService, $scope, $timeout, $log, $http, $mdSidenav) {
    $scope.settings = {};
    $scope.hasData = true;

    $scope.postSettings = function() {
      console.log($scope.settings.data);
      GlobalFcnService.postSettings({
        "collection": "app",
        "data": $scope.settings.data
      });
    };

    $scope.getSettings = function() {
      $scope.hasData = false;
      GlobalFcnService.getSettings().then(function(response) {
        n = response.data;
        $scope.settings.model = n.settingsModel;
        $scope.settings.data = {};
        $scope.settings.data = setData($scope.settings.data, $scope.settings.model, n.userSettings.app);
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
      for (i = 0; i < model.app.length; i++) {
        data[model.app[i].name] = model.app[i].default;
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
