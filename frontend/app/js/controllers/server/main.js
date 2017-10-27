angular.module('app').controller('serverMainCtrl', ['SharedProperties', '$scope',
  '$log', '$timeout', '$filter', '$http',
  function(SharedProperties, $scope, $log, $timeout, $filter, $http) {
    $scope.timer = [];

    $scope.requestData = {
      'cmdcode': false,
      'data': false
    };

    $scope.cb = {
      autoScroll: false
    };

    $scope.debugInfo = '';


    $scope.hiddenKey = function(key) {
      var hkey = [
        'debug', 'info'
      ];
      for (var i = 0; i < hkey.length; i++) {
        if (key === hkey[i]) {
          return true;
        }
      }
      return false;
    };

    var startPollingWs = function(dt) {
      $scope.timer[4] = $timeout(function() {
        if (webSocket.readyState === 1) {
          // console.log(webSocket.readyState);
          webSocket.send(angular.toJson($scope.requestData));
        } else {
          console.log("connecting...");
          startPollingWs(dt);
        }
      }, dt);
    };

    var websocketInit = function() {
      // webSocket = new WebSocket('ws://' + document.domain + ':' + $scope._port + '/app-data/server-main');
      var url = $scope.wsURL + '/app-data/server-main';
      console.log("ws url: ", url);
      webSocket = new WebSocket(url);
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
          if ($scope.jsondata.debug !== '') {
            $scope.debugInfo += $scope.jsondata.debug + '\r\n';
          }

          // var textarea = document.getElementById('texta1');
          // if ($scope.cb.autoScroll && textarea!==undefined) {
          //   textarea.scrollTop = textarea.scrollHeight;
          // }

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

    // $scope.downloadLog = function() {
    //   var text, link, data;
    //   var filename = 'server_log.txt';
    //   text = $scope.debugInfo;
    //   text = 'data:text/plain;charset=utf-8,' + text;
    //
    //   data = encodeURI(text);
    //
    //   link = document.createElement('a');
    //   link.setAttribute('href', data);
    //   link.setAttribute('download', filename);
    //   link.click();
    // };

    $scope.downloadServerLog = function(url) {
      var config = {
        method: 'GET',
        url: $scope.serverURL + url
      };
      $http(config).

      success(function(res) {
          //console.log(res);
          var blob = new Blob([res], {
            type: 'text/plain'
          });
          var url = (window.URL || window.webkitURL).createObjectURL(blob);
          var downloadLink = angular.element('<a></a>');
          downloadLink.attr('href', url);
          downloadLink.attr('download', 'server_log.txt');
          downloadLink[0].click();
        })
        .error(function(res) {

        });
    };


    $scope.sendData = function(cmdcode, data) {
      $scope.requestData.cmdcode = cmdcode;
      $scope.requestData.data = data;
      console.log($scope.requestData);
    };


    $scope.startVideoRecording = function() {
      $http.get($scope.serverURL + '/api/start-rec').
      success(function(data, status, headers, config) {}).
      error(function(data, status, headers, config) {});
    };

    $scope.stopVideoRecording = function() {
      $http.get($scope.serverURL + '/api/stop-rec').
      success(function(data, status, headers, config) {}).
      error(function(data, status, headers, config) {});
    };

    $scope.restart = function() {
      $http.get($scope.serverURL + '/api/restart').
      success(function(data, status, headers, config) {}).
      error(function(data, status, headers, config) {});
    };

    $scope.init = function() {
      var props = SharedProperties.getProperty();
      $scope.serverURL = props.url;
      $scope.wsURL = props.wsurl;
      $scope.timer[0] = $timeout(function() {
        websocketInit();
      }, 500);
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
      closeWebsockets();
      clearTimers();
    });
  }
]);
