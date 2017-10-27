angular.module('app').controller('settingsNodesCtrl', ['SharedProperties', 'GlobalFcnService', '$scope', '$timeout',
  '$log', '$http',
  function(SharedProperties, GlobalFcnService, $scope, $timeout, $log, $http) {
    $scope.nodes = [];
    $scope.error = false;
    $scope.errorMessage = 'error';
    $scope.hasData = true;

    $scope.init = function() {
      $scope.serverURL = SharedProperties.getProperty().url;
      // $scope.getNodeDef();
      $scope.getNodes();
    };

    $scope.getNodes = function() {
      $scope.error = false;
      $scope.hasData = false;
      $http.get($scope.serverURL + '/api/database/nodes').
      then(function(response) {
        var jsonObj = angular.fromJson(response.data);
        $scope.nodes = jsonObj;
        $scope.chunkedNodes = GlobalFcnService.chunk($scope.nodes, 3);
        $scope.hasData = true;
      }, function(err) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        alert('error');
      });
    };

    // $scope.addNode = function() {
    //   var maxid = 0;
    //   if ($scope.nodes !== undefined) {
    //     for (var i = 0; i < $scope.nodes.length; i++) {
    //       if ($scope.nodes[i].SensorId > maxid) {
    //         maxid = $scope.nodes[i].SensorId;
    //       }
    //     }
    //   }
    //   $scope.newNode.SensorId = maxid + 1;
    //   $scope.nodes.push(angular.copy($scope.newNode));
    //   $scope.chunkedNodes = GlobalFcnService.chunk($scope.nodes, 3);
    // };

    $scope.saveNode = function(node) {
      console.log(node);
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/database/nodes', {
        'req': 1,
        'param': node
      }).
      then(function(response) {
        $scope.hasData = true;
        console.log('post success');
        console.log(response.data.result);
        if (response.data.result === SharedProperties.getProperty().constants.RESULT_FAIL) {
          alert('Error adding node');
        } else {
          $scope.getNodes();
        }
      }, function(err) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        alert('error');
      });
    };

    $scope.removeNode = function(node) {
      console.log(node);
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/database/nodes', {
        'req': 2,
        'param': node
      }).
      then(function(response) {
        $scope.hasData = true;
        console.log('post success');
        $scope.getNodes();
      }, function(err) {
        $scope.jsondata = 'error';
        $scope.hasData=true;
        alert('error');
      });
    };

  }
]);
