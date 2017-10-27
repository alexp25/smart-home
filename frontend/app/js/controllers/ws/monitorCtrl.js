angular.module('app').controller('wsMonitorCtrl', ['SharedProperties', '$scope',
  '$log', '$timeout', '$filter', '$http', '$q', '$mdSidenav', 'socket',
  function(SharedProperties, $scope, $log, $timeout, $filter, $http, $q, $mdSidenav, socket) {

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


    $scope.chartData = {
      columns: ['x', 'pump', 'carriage'],
      rows: [
        [1, 0, 0],
        [2, 0, 0],
        [3, 0, 0]
      ],
      timestamp: new Date()
    };


    $scope.ws = 'socketio';

    $scope.requestData = {
      'cmdcode': false,
      'data': false
    };

    var N_TRACES = 3,
      N_POINTS = 50,
      N_SW = 10;

    var polling = true;
    var indexChart = 0;

    $scope.jsonOut = {
      mode: 0,
      pumpCmd: 0,
      carriageCmd: 0,
      carriageDest: 0,
      trackMax: 200,
      sw: [],
      spab_um: 50,
      spab_du: 10
    };

    $scope.hSlider1 = {
      value: 0,
      options: {
        id: 1,
        floor: -255,
        ceil: 255,
        vertical: false,
        onEnd: function(sliderId, modelValue, highValue) {
          //console.log('slide end ' + sliderId);

        },
        onChange: function(sliderId, modelValue, highValue) {
          //console.log('slide ' + sliderId);
          $scope.sendData('CMD_SET_CMD_CARR', $scope.jsonOut.carriageCmd.toString());
        }
      }
    };
    $scope.hSlider2 = {
      value: 0,
      options: {
        id: 2,
        floor: -255,
        ceil: 255,
        vertical: false,
        onEnd: function(sliderId, modelValue, highValue) {
          //console.log('slide end ' + sliderId);

        },
        onChange: function(sliderId, modelValue, highValue) {
          //console.log('slide ' + sliderId);
          $scope.sendData('CMD_SET_CMD_PUMP', $scope.jsonOut.pumpCmd.toString());
        }
      }
    };


    $scope.chart = [{
      ntraces: 2,
      options: {
        labels: ['pump command', 'carriage command'],
        xAxisType: 'numeric',
        visible: [true, true],
        range: [-255, 255],
        xAxisTickInterval: 10,
        yAxisTickInterval: 100
      }
    }, {
      ntraces: 1,
      options: {
        labels: ['carriage location'],
        xAxisType: 'numeric',
        visible: [true],
        range: [0, 200],
        xAxisTickInterval: 10,
        yAxisTickInterval: 50
      }
    }];


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
      $scope.settings = props.ws.settings;


      $scope.constants = props.constants;

      for (var i = 0; i < N_SW; i = i + 1) {
        $scope.jsonOut.sw[i] = {
          index: i,
          name: 'sw ' + i,
          value: false
        };
      }
      console.log($scope.jsonOut);

      if ($scope.ws === 'socketio') {
        socket.connect();
        socket.on('ws_control_data', function(data) {
          getSocketData(angular.fromJson(data));
        });
        startPollingWs_socketio();
      } else {
        $scope.timer[4] = $timeout(function() {
          websocketInit();
        }, 500);
      }
      $scope.signalUpdate = !$scope.signalUpdate;
    };


    var startPollingWs_socketio = function() {
      $scope.timer[1] = $timeout(function() {
        socket.emit('ws_control_get', {
          message: ''
        }, function(data) {
          startPollingWs_socketio();
        });

      }, 1);
    };

    var getSocketData = function(jsondata) {
      if (jsondata.info !== "no data") {
        $scope.jsondata = jsondata;
        // console.log($scope.jsondata);

        $scope.infoList = [{
          name: 'Mode',
          value: $scope.jsondata.mode
        }, {
          name: 'System time',
          value: $scope.jsondata.systemTime
        }, {
          name: 'Current plant',
          value: $scope.jsondata.currentPlant
        }, {
          name: 'Program start',
          value: $scope.jsondata.systemOffRem
        }, {
          name: 'Plant finish',
          value: $scope.jsondata.systemOnRem
        }];

        $scope.signalUpdate = !$scope.signalUpdate;
        // updateChart($scope.jsondata);
      }
    };

    var insertEnd = function(arr, val) {
      for (var i = 0; i < arr.length; i++) {
        arr[i] = arr[i + 1];
      }
      arr[arr.length - 1] = val;
    };

    var updateChart = function(jsonObj) {
      /** not working */
      var newSample = [indexChart, jsonObj.pumpCmd, jsonObj.carriageCmd];
      if (indexChart < 25) {
        $scope.chartData.rows[indexChart] = newSample;
        indexChart++;
      } else {
        insertEnd($scope.chartData.rows, newSample);
      }
      // console.log($scope.chartData.rows);
      $scope.chartData.timestamp = new Date();
    };

    var websocketInit = function() {
      // webSocket = new WebSocket('ws://' + document.domain + ':' + $scope._port + '/app-data');
      webSocket = new WebSocket($scope.wsURL + '/app-data');
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
          var jsondata = angular.fromJson(event.data);

          getSocketData(jsondata);

          $scope.timer[2] = $timeout(function() {
            if (webSocket.readyState === 1) {
              webSocket.send(angular.toJson($scope.requestData));
              $scope.requestData.cmdcode = false;
              $scope.requestData.data = false;
            } else {
              startPollingWs(100);
            }
          }, 1);
        });
      };
    };

    $scope.sendData = function(cmdcode, data) {
      $scope.requestData.cmdcode = cmdcode;
      $scope.requestData.data = data;
      console.log($scope.requestData);

      if ($scope.ws === 'socketio') {
        socket.emit('ws_control_set', angular.toJson($scope.requestData));
      } else {

      }
    };

    $scope.toggleStream = function(enable) {
      if (enable === undefined) {
        $scope.enableStream = !$scope.enableStream;
      } else {
        $scope.enableStream = enable;
      }


      if ($scope.enableStream === true) {
        $scope.initialized2 = false;
      } else {
        $timeout(function() {
          $scope.initialized2 = true;
        }, 300);
      }
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

      if ($scope.ws === 'socketio') {
        console.log('disconnect');
        socket.emit('disconnect_request', '');
      } else {
        closeWebsockets();
      }
      //clearEventListeners();

    });

  }
]);
