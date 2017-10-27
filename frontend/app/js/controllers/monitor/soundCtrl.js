angular.module('app').controller('monitorSoundCtrl', ['SharedProperties', '$scope',
  '$log', '$timeout', '$filter', '$http', '$q', '$mdSidenav',
  function(SharedProperties, $scope, $log, $timeout, $filter, $http, $q, $mdSidenav) {

    $scope.enableStream = false;

    $scope.getStatus = true;
    $scope.initialized = false;
    $scope.mobile = false;

    $scope.chupdate = false;

    $scope.timer = [];
    $scope.array = [
      []
    ];


    $scope.chartData1 = {
      cutn: 10,
      columns: ['x', 'scope'],
      rows: [
        [1, 20],
        [2, 20],
      ],
      timestamp: new Date()
    };

    $scope.chartData2 = {
      columns: ['x', 'spectrum'],
      rows: [
        [1, 30],
        [2, 30],
      ],
      timestamp: new Date()
    };

    $scope.requestData = {
      'cmdcode': false,
      'data': false
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
          // $scope.sendData('CMD_SET_CMD_CARR', $scope.jsonOut.carriageCmd.toString());
        }
      }
    };



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
      $scope.timer[2] = $timeout(function() {
        websocketInit();
      }, 500);
    };

    $scope.startSound = function() {
      $scope.error = false;
      $scope.hasData = false;
      $http.get($scope.serverURL + '/api/start-sound-a');
    };
    $scope.stopSound = function() {
      $scope.error = false;
      $scope.hasData = false;
      $http.get($scope.serverURL + '/api/stop-sound-a');
    };

    var websocketInit = function() {
      webSocket = new WebSocket($scope.wsURL + '/app-data/monitor-sound');
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
          $scope.chupdate = !$scope.chupdate;


          var rows = [];
          for (i = 0; i < $scope.jsondata.rawData.length; i++) {
            rows[i] = [i, $scope.jsondata.rawData[i]];
          }
          $scope.chartData1.rows = rows;
          $scope.chartData1.timestamp = new Date();

          rows = [];
          for (i = 0; i < $scope.jsondata.rawFFT.length; i++) {
            rows[i] = [i, $scope.jsondata.rawFFT[i]];
          }
          $scope.chartData2.rows = rows;
          $scope.chartData2.timestamp = new Date();


          // console.log($scope.jsondata);
          //$scope.gridOptions.data = $scope.jsondata.clientList;
          $scope.timer[4] = $timeout(function() {
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

    $scope.$on("$destroy", function() {
      clearTimers();
      closeWebsockets();
    });

  }
]);
