angular.module('app').controller('monitorViewAllCtrl', ['SharedProperties', 'GlobalFcnService', '$scope',
  '$log', '$timeout', '$filter', '$http', '$q', '$mdSidenav',
  function(SharedProperties, GlobalFcnService, $scope, $log, $timeout, $filter, $http, $q, $mdSidenav) {

    $scope.enableStream = false;

    $scope.getStatus = true;
    $scope.initialized = false;
    $scope.mobile = false;

    $scope.signalUpdate = false;
    $scope.signalUpdate2 = false;
    $scope.timer = [];
    $scope.array = [
      []
    ];

    $scope.test = {
      'val': 5
    };

    $scope.requestData = {
      'cmdcode': "SERVER_REQUEST",
      'data': {
        "nodeId": -1
      }
    };

    $scope.user = {
      cmdValue: 0
    };

    $scope.clientList = [];
    $scope.clientSelectionList = [];

    $scope.dataFlag = false;

    $scope.hasData = true;


    var startPollingWs = function(dt) {
      $scope.timer[1] = $timeout(function() {
        if (webSocket.readyState === 1) {
          // console.log(webSocket.readyState);
          webSocket.send(angular.toJson($scope.requestData));
        } else {
          console.log("connecting...");
          startPollingWs(dt);
        }
      }, dt);
    };

    $scope.init = function() {
      var props = SharedProperties.getProperty();
      $scope.serverURL = props.url;
      $scope.wsURL = props.wsurl;
      $scope._port = props.port;
      $scope.hasData = false;
      GlobalFcnService.getSettings().then(function(response) {
        n = response.data;
        $scope.settings = n.data;
        $scope.nodeModelDB = n.nodeModelDB;
        console.log($scope.settings);
      }, function(err) {
        // handle possible errors that occur when making the request.
        console.log(err);
        $scope.hasData = true;
        alert('error');
      });

      // $scope.getNodes();
      $scope.timer[2] = $timeout(function() {
        websocketInit();
      }, 500);
      $scope.signalUpdate = !$scope.signalUpdate;
    };


    $scope.getNodes = function() {
      $scope.error = false;
      $scope.hasData = false;
      $http.get($scope.serverURL + '/api/database/nodes').
      then(function(response) {
          var jsonObj = angular.fromJson(response.data);
          $scope.nodes = jsonObj;
          $scope.hasData = true;
        },
        function(err) {
          $scope.jsondata = 'error';
          $scope.hasData = true;
          alert('error');
        });
    };


    var websocketInit = function() {
      // location.port
      webSocket = new WebSocket($scope.wsURL + '/app-data/monitor-view');

      webSocket.onopen = function(event) {
        console.log("webSocket open");
        startPollingWs(100);
      };
      webSocket.onclose = function(event) {
        console.log("webSocket closed");
        $scope.$apply(function() {
          $scope.timer[3] = $timeout(function() {
            websocketInit();
          }, 1000);
        });
      };
      webSocket.onmessage = function(event) {
        $scope.$apply(function() {
          $scope.jsonstr = event.data;
          $scope.jsondata = angular.fromJson(event.data);
          //$scope.gridOptions.data = $scope.jsondata.clientList;


          if ($scope.clientList.length !== $scope.jsondata.clientList.length) {
            // refresh elements (reload)
            console.log("client list updated");
            $scope.dataFlag = false;
            // $scope.clientList = clientSort($scope.jsondata.clientList);
            $scope.updateClientIdList($scope.jsondata.clientList);
          } else {
            $scope.dataFlag = true;
            // $scope.clientList = clientSort($scope.jsondata.clientList);
          }

          $scope.clientList = $scope.jsondata.clientList;

          if ($scope.jsondata.clientData !== undefined) {
            $scope.clientData = $scope.jsondata.clientData;
          }

          $scope.timer[2] = $timeout(function() {
            if (webSocket.readyState === 1) {
              webSocket.send(angular.toJson($scope.requestData));
              $scope.requestData.cmdcode = "SERVER_REQUEST";
              $scope.requestData.data = {
                "nodeId": -1
              };
            } else {
              startPollingWs(100);
            }
          }, 1);
        });
      };
    };

    // $scope.$on("slideEnded", function(sliderObject) {
    //   console.log("slideEnded ");
    //   console.log(sliderObject);
    //   console.log(sliderObject.targetScope.slider.options.id);
    //   console.log(sliderObject.targetScope.rzSliderModel);
    //   // user finished sliding a handle
    // });
    $scope.sliderOnChange = function(sliderId, modelValue, highValue, pointerType) {
      // console.log(sliderId);
      // console.log(modelValue);
      $scope.sendData('DEVICE_CMD', {
        'nodeId': $scope.selectedNodeId,
        'fback': sliderId.toString() + ',' + modelValue.toString()
      });
    };

    $scope.$watch('selectedNodeId', function(newValue, oldValue) {
      $scope.selectedNode = findClientWithId($scope.clientList, parseInt(newValue));
      $scope.selectedNodeIndex = findClientIndexWithId($scope.clientList, parseInt(newValue));
      console.log($scope.selectedNode);
      $scope.showCmd = false;
      $timeout(function() {
        $scope.showCmd = true;
      });
      // $scope.sendData("SERVER_CMD", {
      //   "cmd": "SYNC_DEVICE_CONTROLS"
      // });
    });

    var findClientWithId = function(clientList, id) {
      var client = {};
      console.log(clientList);
      if (clientList) {
        for (var i = 0; i < clientList.length; i++) {
          if (clientList[i].id === id) {
            client = clientList[i];
            break;
          }
        }
      }
      return client;
    };

    var findClientIndexWithId = function(clientList, id) {
      var clientIndex = 0;
      if (clientList) {
        for (var i = 0; i < clientList.length; i++) {
          if (clientList[i].id === id) {
            clientIndex = i;
            break;
          }
        }
      }
      return clientIndex;
    };

    $scope.updateClientIdList = function(clientList) {
      var append = true;
      var remove = true;
      var i, j;
      // remove
      for (i = 0; i < $scope.clientSelectionList.length; i++) {
        remove = true;
        for (j = 0; j < clientList.length; j++) {
          if (clientList[j].id === $scope.clientSelectionList[i].id) {
            remove = false;
          }
        }
        if (remove) {
          $scope.clientSelectionList.splice(i);
        }
      }

      // append
      for (i = 0; i < clientList.length; i++) {
        append = true;
        for (j = 0; j < $scope.clientSelectionList.length; j++) {
          if (clientList[i].id === $scope.clientSelectionList[j].id) {
            append = false;
          }
        }
        if (append) {
          $scope.clientSelectionList.push({
            "id": clientList[i].id,
            "view": true
          });
        }

      }

      $scope.clientSelectionList.sort();
    };

    var clientSort = function(clientList) {
      function compare(a, b) {
        if (a.id < b.id) {
          return -1;
        }
        if (a.id > b.id) {
          return 1;
        }
        return 0;
      }
      return clientList.sort(compare);
    };

    $scope.toggleNode = function(nodeid) {

    };
    $scope.checkNode = function(nodeid) {

    };

    $scope.sendData = function(cmdcode, data) {
      console.log('send');
      console.log(cmdcode);
      console.log(data);
      $scope.requestData.cmdcode = cmdcode;
      $scope.requestData.data = data;
    };

    $scope.sendDeviceData = function(nodeId, cmd) {
      if (cmd.minValue !== undefined) {
        if (cmd.value < cmd.minValue) {
          cmd.value = cmd.minValue;
        }
      }
      if (cmd.maxValue !== undefined) {
        if (cmd.value > cmd.maxValue) {
          cmd.value = cmd.maxValue;
        }
      }
      $scope.sendData('DEVICE_CMD', {
        'nodeId': nodeId,
        'fback': cmd.code.toString() + ',' + cmd.value.toString()
      });
    };

    var clearTimers = function() {
      for (var i = 0; i < $scope.timer.length; i++) {
        if ($scope.timer[i] !== undefined) {
          console.log("clear timer " + i.toString());
          $timeout.cancel($scope.timer[i]);
        }
      }
    };

    var closeWebsockets = function() {
      webSocket.close();
    };

    /*  var removeEventListeners = function(){
        window.removeEventListener("keydown", $scope.keyPress, false);
      };*/


    $scope.$on("$destroy", function() {
      clearTimers();
      closeWebsockets();
      //clearEventListeners();

    });

  }
]);
