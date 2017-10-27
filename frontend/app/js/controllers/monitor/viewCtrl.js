angular.module('app').controller('monitorViewCtrl', ['SharedProperties', 'GlobalFcnService', '$scope',
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


    $scope.gaugeData = {
      columns: [
        ['flow', 10]
      ],
      timestamp: new Date()
    };

    $scope.test = {
      'val': 5
    };

    $scope.requestData = {
      'cmdcode': false,
      'data': false
    };

    $scope.user = {
      cmdValue: 0
    };

    $scope.clientList = [];
    $scope.clientBasicViewList = [];
    $scope.dataFlag = false;
    $scope.hasData = false;

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
      $scope._port = props.port;
      $scope.serverURL = props.url;
      $scope.wsURL = props.wsurl;
      $scope.hasData = false;
      GlobalFcnService.getSettings().then(function(response) {
        n = response.data;
        $scope.settings = n.userSettings;
        $scope.nodeModelDB = n.nodeModelDB;
        console.log($scope.settings);
      }, function(err) {
        // handle possible errors that occur when making the request.
        $scope.hasData = true;
        //alert('error');
      });

      $scope.timer[2] = $timeout(function() {
        websocketInit();
      }, 500);
      $scope.signalUpdate = !$scope.signalUpdate;
    };


    $scope.sliderOnChange = function(sliderId, modelValue, highValue, pointerType) {
      $scope.sendData('DEVICE_CMD', {
        'nodeId': $scope.clientList[$scope.selectedNodeIndex].id,
        'fback': sliderId.toString() + ',' + modelValue.toString()
      });
    };

    var websocketInit = function() {
      // webSocket = new WebSocket('ws://' + document.domain + ':' + $scope._portlocation.port + '/app-data/monitor-view');
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

          if ($scope.jsondata.clientList !== undefined) {
            if ($scope.clientList.length !== $scope.jsondata.clientList.length) {
              // refresh elements (reload)
              // refresh client array and update client visible state
              console.log("client list updated");
              $scope.dataFlag = false;

            } else {
              $scope.dataFlag = true;
            }

            $scope.clientBasicViewList = updateClientBasicViewList($scope.jsondata.clientList, false);
            $scope.clientBasicViewList = $scope.addProperty($scope.clientBasicViewList, false);
            // console.log($scope.clientBasicViewList);
            $scope.chkClientBasicViewList = GlobalFcnService.chunk($scope.clientBasicViewList, 3);

            $scope.clientList = $scope.jsondata.clientList;

            if ($scope.jsondata.clientData !== undefined) {
              $scope.clientData = $scope.jsondata.clientData;

            }

            // default selection
            if ($scope.selectedNodeIndex === undefined) {
              $scope.selectedNodeIndex = 0;
              $scope.selectNode(0);
            }
            // refresh data view if selected node id changed
            if ($scope.clientData !== undefined) {
              if ($scope.clientData.id !== $scope.prev_id) {
                $scope.prev_id = $scope.clientData.id;
                $scope.dataFlag = false;
                $timeout(function() {
                  $scope.dataFlag = true;
                }, 1);
              }
            }

            // console.log($scope.clientData);
          }

          $scope.timer[2] = $timeout(function() {
            if (webSocket.readyState === 1) {
              webSocket.send(angular.toJson($scope.requestData));

              if ($scope.selectedNodeIndex !== undefined) {
                $scope.requestData.cmdcode = "SERVER_REQUEST";
                $scope.requestData.data = {
                  "nodeId": $scope.selectedNodeIndex
                };
              } else {
                $scope.requestData.cmdcode = false;
                $scope.requestData.data = false;
              }
            } else {
              startPollingWs(100);
            }
          }, 1);
        });
      };
    };


    $scope.addProperty = function(array, replace) {
      var i = 0;
      angular.forEach(array, function(eachObj) {
        i += 1;
        if (!replace) {
          if (eachObj.selected === undefined) {
            console.log("add property");
            eachObj.selected = 'false';
          }
        } else {
          eachObj.selected = 'false';
        }

      });
      return array;
    };

    $scope.$on("slideEnded", function(sliderId) {
      console.log("slideEnded ");
      console.log(sliderId);
      // user finished sliding a handle
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

    var updateClientBasicViewList = function(clientList, sortFlag) {
      var append = true;
      var remove = true;
      var i, j;
      var clientBasicViewList = [];
      // remove
      for (i = 0; i < clientBasicViewList.length; i++) {
        remove = true;
        for (j = 0; j < clientList.length; j++) {
          if (clientList[j].id === clientBasicViewList[i].id) {
            remove = false;
          }
        }
        if (remove) {
          clientBasicViewList.splice(i);
        }
      }
      // append
      for (i = 0; i < clientList.length; i++) {
        append = true;
        for (j = 0; j < clientBasicViewList.length; j++) {
          if (clientList[i].id === clientBasicViewList[j].id) {
            append = false;
          }
        }
        if (append) {
          clientBasicViewList.push({
            "id": clientList[i].id,
            "type": clientList[i].type,
            "class": clientList[i].class,
            "ip": clientList[i].ip,
            "selected": false,
            "index": i
          });
        }
      }

      if (sortFlag) {
        clientBasicViewList.sort(function(a, b) {
          return a.id - b.id;
        });
      }

      return clientBasicViewList;
    };

    $scope.selectNode = function(index) {
      // deselect all other nodes
      for (var i = 0; i < $scope.clientBasicViewList.length; i++) {
        $scope.clientBasicViewList[i].selected = false;
      }
      $scope.clientBasicViewList[index].selected = true;
      $scope.selectedNodeIndex = $scope.clientBasicViewList[index].index;
      console.log('selected node index: ' + index + " sorted index: " + $scope.clientBasicViewList[index].index + ' id: ' + $scope.clientList[index].id);
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

    $scope.sendData = function(cmdcode, data) {
      // console.log('send');
      // console.log(cmdcode);
      // console.log(data);
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
      var cmdstring;
      cmdstring = cmd.code.toString();
      if (cmd.value !== undefined) {
        cmdstring += ',' + cmd.value.toString();
      }

      $scope.sendData('DEVICE_CMD', {
        'nodeId': nodeId,
        'fback': cmdstring
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
