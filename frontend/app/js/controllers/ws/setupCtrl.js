angular.module('app').controller('wsSetupCtrl', ['SharedProperties', 'PollingService', 'GlobalFcnService', '$scope',
  '$log', '$http', '$q',
  function(SharedProperties, PollingService, GlobalFcnService, $scope, $log, $http, $q) {
    $scope.name = 'alex raspberry PI B+ web server';
    $scope.jsondata = 'null';

    $scope.hasData = true;

    $scope.wsSettings = {};
    $scope.cmdString = 'CMD_SET_MODE_AUTO';
    $scope.constants = {};
    $scope.nodes = [];

    $scope.newControlSettings = {};
    $scope.controlType = ['pid', 'spab'];

    $scope.init = function() {
      var props = SharedProperties.getProperty();
      $scope.serverURL = props.url;
      $scope.settings = props.ws.settings;
      $scope.constants = props.constants;
      $scope.getWsSettings();
    };


    $scope.sendData = function(cmd, body) {
      var dataObj = {
        cmd: cmd,
        data: body,
      };
      console.log(dataObj);
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/bluetooth-serial/send', dataObj).
      then(function(response) {
        console.log('data sent');
        $scope.hasData = true;
      }, function(response) {
        console.log('server error');
        $scope.hasData = true;
        //alert('error');
      });
    };


    $scope.getWsSettings = function() {
      $scope.hasData = false;
      $http.get($scope.serverURL + '/api/ws/setup').
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);
        console.log(jsonObj);
        $scope.wsSettings = jsonObj;
        $scope.hasData = true;
      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        //alert('error');
      });
    };


    $scope.syncTime = function() {
      var dataObj = {};
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/ws/setup/sync-time', dataObj).
      then(function(response) {
        console.log('data sent');
        $scope.hasData = true;
      }, function(response) {
        console.log('server error');
        $scope.hasData = true;
        //alert('error');
      });
    };
  }
]);
