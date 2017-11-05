angular.module('app').controller('wsSetupAdvancedCtrl', ['SharedProperties', 'PollingService', 'GlobalFcnService', '$scope',
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
      $scope.getControlSettings();
    };

    var setData = function(data, model) {
      var i, j;
      // set default values from model
      for (i = 0; i < model.length; i++) {
        data[model[i].name] = model[i].default;
      }
      return data;
    };

    $scope.addControlSettingsNode = function() {
      var maxid = 0;
      $scope.newControlSettings = setData($scope.newControlSettings, $scope.settingsModel);

      if ($scope.nodes !== undefined) {
        for (var i = 0; i < $scope.nodes.length; i++) {
          if ($scope.nodes[i].sensorId > maxid) {
            maxid = $scope.nodes[i].sensorId;
          }
        }
      }
      $scope.newControlSettings.sensorId = maxid + 1;

      $scope.nodes.push(angular.copy($scope.newControlSettings));
      $scope.chunkedNodes = GlobalFcnService.chunk($scope.nodes, 3);
    };

    $scope.saveNode = function(node) {
      console.log(node);
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/database/control-settings', {
        'req': 1,
        'param': node
      }).then(function(data) {
        $scope.hasData = true;
        console.log('post success');
        console.log(data.data.result);
        $scope.getControlSettings();
      }).catch(function(data) {
        console.log('post error');
        $scope.hasData = true;
        //alert('error');
      });
    };
    $scope.removeNode = function(node) {
      console.log(node);
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/database/control-settings', {
        'req': 2,
        'param': node
      }).
      then(function(data) {
        $scope.hasData = true;
        console.log('post success');
        $scope.getControlSettings();
      }).
      catch(function(data) {
        console.log('post error');
        $scope.hasData = true;
        //alert('error');
      });
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
          $scope.settingsModel = jsonObj.data.settingsModel;
          $scope.chunkedNodes = GlobalFcnService.chunk($scope.nodes, 3);
          $scope.hasData = true;
        })
        .catch(function(data) {
          $scope.hasData = true;
          //alert('error');
        });
      return promise;
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
