angular.module('app').controller('wsAcsCtrl', ['$scope', 'SharedProperties', 'GlobalFcnService', '$timeout',
  '$log', '$http', '$mdSidenav', '$q',
  function($scope, SharedProperties, GlobalFcnService, $timeout, $log, $http, $mdSidenav, $q) {
    $scope.hasData = true;
    $scope.initialized = false;

    $scope.chartData = {
      columns: ['x', 'input', 'output', 'setpoint'],
      rows: [
        [1, 10, 40, 68],
        [2, 20, 60, 68],
        [3, 30, 65, 68],
      ],
      timestamp: new Date()
    };

    $scope.init = function() {
      $scope.serverURL = SharedProperties.getProperty().url;
      GlobalFcnService.getSettings().then(function(response) {
        console.log("settings");
        $scope.settings = response.data.userSettings.monitor;
        console.log($scope.settings);
        $scope.getControlSettings().then(function(msg) {
          $scope.getSelectedControlSettings().then(function(msg) {
            $scope.getData();
          });
        });
      });

    };


    $scope.getData = function() {
      $scope.hasData = false;
      console.log('getData: ');
      $http.get($scope.serverURL + '/api/database/control', {
        params: {
          s_id: $scope.settings.acs_sid,
          n: $scope.settings.acs_lastNData
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);
        console.log(jsonObj);
        // console.log(jsonObj[0].ts);
        $scope.jsonObj = jsonObj;
        $scope.info = data.info;
        var i;

        if (jsonObj !== false) {
          $scope.hasData = true;

          $scope.displayData = false;
          var rows = [];
          var uk, yk, rk;
          for (i = 0; i < jsonObj.length; i++) {
            uk = Math.floor(100 * (jsonObj[i].uk1 - $scope.controlSettings.umin) / ($scope.controlSettings.umax - $scope.controlSettings.umin));
            yk = Math.floor(100 * (jsonObj[i].yk - $scope.controlSettings.ymin) / ($scope.controlSettings.ymax - $scope.controlSettings.ymin));
            rk = Math.floor(100 * (jsonObj[i].rk - $scope.controlSettings.ymin) / ($scope.controlSettings.ymax - $scope.controlSettings.ymin));
            rows[i] = [new Date(jsonObj[i].ts), uk, yk, rk];
          }
          $scope.chartData.rows = rows;
          $scope.chartData.timestamp = new Date();

          $timeout(function() {
            $scope.displayData = true;
          });

          console.log('dataset updated');
        }
      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        //alert('error');
      });
    };

    $scope.getControlSettings = function() {
      $scope.hasData = false;
      var promise = $http.get($scope.serverURL + '/api/database/control-settings', {
        params: {
          sensorId: -1
        }
      }).
      then(function(data) {
          var jsonObj = angular.fromJson(data);
          console.log(jsonObj);
          $scope.nodes = jsonObj.data.data;
          $scope.hasData = true;
        })
        .catch(function(data) {
          $scope.hasData = true;
          //alert('error');
        });
      return promise;
    };

    $scope.getSelectedControlSettings = function() {
      $scope.hasData = false;
      var promise = $http.get($scope.serverURL + '/api/database/control-settings', {
        params: {
          sensorId: $scope.settings.acs_sid
        }
      }).
      then(function(data) {
          var jsonObj = angular.fromJson(data);
          console.log("control settings");
          $scope.controlSettings = jsonObj.data.data[0];
          console.log($scope.controlSettings);
          $scope.hasData = true;
        })
        .catch(function(data) {
          $scope.hasData = true;
          //alert('error');
        });
      return promise;
    };

    $scope.$on('$destroy', function(event) {});
  }
]);
