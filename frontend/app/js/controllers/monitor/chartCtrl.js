angular.module('app').controller('monitorChartCtrl', ['SharedProperties', 'GlobalFcnService', '$scope', '$timeout',
  '$log', '$http', '$mdSidenav', '$q',
  function (SharedProperties, GlobalFcnService, $scope, $timeout, $log, $http, $mdSidenav, $q) {
    $scope.nodes = [];
    $scope.startDate = new Date();
    $scope.endDate = new Date();
    var zoomLevel = 10;
    $scope.chupdate = false;
    $scope.channels = [1, 2];
    $scope.weatherRequests = [{
      'id': 0,
      'name': 'forecast',
      'url': 'http://api.openweathermap.org/api/2.5/forecast/daily'
    }, {
      'id': 1,
      'name': 'current',
      'url': 'http://api.openweathermap.org/api/2.5/weather'
    }];

    $scope.locations = [{
      'name': 'Bucharest'
    }];

    $scope.chartData = {
      refresh: true,
      columns: ['x', 'data'],
      rows: [
        // [1, 37.8],
        // [2, 30.9],
        // [3, 25.4],
        // [4, 11.7],
        // [5, 11.9],
        // [6, 8.8],
        // [7, 7.6],
        // [8, 12.3],
        // [9, 16.9],
        // [10, 12.8],
        // [11, 5.3],
        // [12, 6.6],
        // [13, 4.8],
        // [14, 4.2]
      ],
      timestamp: new Date()
    };


    $scope.getWeatherData = function () {
      $scope.weatherRequest.url = $scope.selectedWeatherReqType.url;
      $scope.weatherRequest.params.q = $scope.selectedLocation.name;
      $scope.hasWeatherData = false;
      $http($scope.weatherRequest)
        .then(function (response) {
          $scope.weatherData = response.data;
          console.log($scope.weatherData);
          $scope.hasWeatherData = true;
        }).
        catch(function (response) {
          $scope.hasWeatherData = true;
          // alert('error');
        });
    };

    $scope.series = [{
      'name': '1',
      'value': 0
    }];

    R_UNTIL_SELECTED = 0;
    R_UNTIL_MOST_RECENT = 1;
    R_LATEST_TIME = 2;
    R_LATEST_SAMPLE = 3;

    $scope.settings = {};
    $scope.requestSettings = {
      options: [{
        label: 'latest data (time)',
        value: R_LATEST_TIME
      }, {
        label: 'latest data (samples)',
        value: R_LATEST_SAMPLE
      }]
    };
    $scope.timer = [];

    $scope.autoUpdate = function () {
      if ($scope.settings.updateRate !== undefined) {
        $scope.timer[0] = $timeout(function () {
          $scope.userRequestData();
          $scope.autoUpdate();
        }, $scope.settings.updateRate * 1000);
      }
    };

    $scope.autoUpdateWeather = function () {
      $scope.timer[1] = $timeout(function () {
        $scope.getWeatherData();
        $scope.autoUpdateWeather();
      }, 3600 * 1000);
    };

    $scope.noAutoUpdate = function () {
      $scope.settings.autoUpdate = false;
      $timeout.cancel($scope.timer[0]);
      $timeout.cancel($scope.timer[1]);
    };

    $scope.resetAutoUpdate = function () {
      $timeout.cancel($scope.timer[0]);
      $timeout.cancel($scope.timer[1]);
      $scope.autoUpdate();
    };

    $scope.userRequestData = function () {
      var param;
      getMaxChan($scope.nodes);
      switch ($scope.settings.requestType) {
        case R_UNTIL_SELECTED:
          param = {
            'startDate': $scope.startDate,
            'endDate': $scope.endDate,
            'interval': {
              'h': $scope.settings.reqtime_h,
              'm': $scope.settings.reqtime_m,
              's': 0
            },
            'sensorId': $scope.settings.sensorId,
            'channelId': $scope.settings.channelId
          };
          getData('date1', param);
          break;
        case R_UNTIL_MOST_RECENT:
          param = {
            'startDate': $scope.startDate,
            'sensorId': $scope.settings.sensorId,
            'channelId': $scope.settings.channelId
          };
          getData('date2', param);
          break;
        case R_LATEST_SAMPLE:
          param = {
            'n': $scope.settings.lastNData,
            'sensorId': $scope.settings.sensorId,
            'channelId': $scope.settings.channelId
          };
          getData('nlast', param);
          break;
        case R_LATEST_TIME:
          param = {
            'h': $scope.settings.lastHData,
            'sensorId': $scope.settings.sensorId,
            'channelId': $scope.settings.channelId
          };
          getData('last', param);
          break;
        default:
          break;
      }
      if ($scope.settings.autoUpdate) {
        $scope.startDate = new Date();
        $scope.endDate = new Date();
      }
    };

    // $scope.yzoom = function(zoomin) {
    //   if (zoomin === 0) {
    //     zoomLevel += 10;
    //   } else {
    //     if (zoomLevel >= 20) {
    //       zoomLevel -= 10;
    //     }
    //   }
    //   chartRefresh();
    // };

    var getData = function (reqType, param1) {
      if (reqType === undefined || param1 === undefined) {
        return;
      }
      $scope.hasData = false;

      console.log('getData: ', reqType, param1);
      $http.get($scope.serverURL + '/api/database/sensors/' + reqType, {
        params: {
          param: param1
        }
      }).
        then(function (data) {
          var jsonObj = angular.fromJson(data.data);
          console.log(jsonObj);

          var maxplotlength = 1000;
          if ($scope.settings.maxPlotLength !== undefined) {
            maxplotlength = $scope.settings.maxPlotLength;
          }

          $scope.jsonObj = jsonObj;
          $scope.info = data.info;
          var i;

          console.log("data length: ", jsonObj.length);
          console.log("plot length: ", maxplotlength);
          // console.log(jsonObj[0].ts);


          if (jsonObj !== false && jsonObj.length > 0) {
            $scope.hasData = true;

            $scope.displayData = false;
            var rows = [];

            for (i = 0; i < jsonObj.length; i++) {
              if (i > maxplotlength) {
                break;
              }
              rows[i] = [new Date(jsonObj[i].ts), jsonObj[i].value];
            }

            // $scope.chartData.columns[1] = 'sensor ' + jsonObj[0].s_id + ' channel ' + jsonObj[0].s_chan;
            $scope.chartData.columns[1] = 'data';
            $scope.chartData.rows = rows;
            $scope.chartData.timestamp = new Date();


            if (jsonObj.length > maxplotlength) {
              console.log("Maximum plot length exceeded. Showing only first " + maxplotlength.toString() + " records");
              // alert("Maximum plot length exceeded. Showing only first " + maxplotlength.toString() + " records");
            }

            $timeout(function () {
              $scope.displayData = true;
            });

            console.log('dataset updated');
          }
        }).
        catch(function (data) {
          $scope.jsondata = 'error';
          $scope.hasData = true;
          //alert('error');
        });
    };



    // var updateInfo = function() {
    //   console.log('update info');
    //   if ($scope.valueArray) {
    //
    //     var series = $scope.valueArray;
    //     var avg = Math.floor(average(series));
    //     $scope.localData = {
    //       'last': series[series.length - 1],
    //       'max': Math.max.apply(null, series),
    //       'min': Math.min.apply(null, series),
    //       'avg': avg
    //     };
    //     $scope.chart[0].options.maxThreshold = avg;
    //   }
    // };

    // function average(v) {
    //   var avg = 0;
    //   for (var i = 0; i < v.length; i++) {
    //     avg += v[i];
    //   }
    //   return avg / v.length;
    // }

    $scope.postSettings = function () {
      updateUserOptions();
      GlobalFcnService.postSettings($scope.settings);
    };

    function getMaxChan(nodes) {
      nodes.forEach(function (element) {
        if (element.s_id === $scope.settings.sensorId) {
          $scope.settings.channelMax = element.n_chan;
        }
      });
      if ($scope.settings.channelId > $scope.settings.channelMax) {
        $scope.settings.channelId = $scope.settings.channelMax;
      }
    }

    $scope.init = function () {
      var props = SharedProperties.getProperty();
      $scope.selectedWeatherReqType = $scope.weatherRequests[1];
      $scope.selectedLocation = $scope.locations[0];
      $scope.serverURL = props.url;
      $scope.weatherRequest = {
        method: 'GET',
        url: $scope.selectedWeatherReqType.url,
        params: {
          q: $scope.selectedLocation.name,
          mode: 'json',
          units: 'metric',
          cnt: '7',
          appid: '13d3396479dc92a69c579d67bd4835cc'
        }
      };


      GlobalFcnService.getSettings().then(function (response) {
        $scope.settings = response.data.userSettings.monitor;
        console.log("settings");
        console.log($scope.settings);
        $scope.weatherRequest.params.appid = $scope.settings.appid;

        $scope.getNodes().then(function (res) {
          // $scope.settings.channelId = 0;
          console.log("get nodes done");
          // getMaxChan(res);

          $scope.userRequestData();
          if ($scope.settings.weatherData === true) {
            $scope.getWeatherData();
          }
          if ($scope.settings.autoUpdate) {
            $scope.autoUpdate();
            if ($scope.settings.weatherData === true) {
              $scope.autoUpdateWeather();
            }
          }
          $scope.initialized = true;
        });
      }).catch(function(err) {
        console.log(err);
      });
    };


    $scope.getNodes = function () {
      var deferred = $q.defer();
      $scope.error = false;
      //  $scope.hasData = false;
      $http.get($scope.serverURL + '/api/database/nodes').
        then(function (data) {
          var jsonObj = angular.fromJson(data.data);
          $scope.nodes = jsonObj;
          console.log($scope.nodes);
          deferred.resolve(jsonObj);
        }).
        catch(function (data) {
          $scope.jsondata = 'error';
          $scope.hasData = true;
          deferred.reject(false);
          //alert('error');
        });
      return deferred.promise;
    };

    var clearTimers = function () {
      for (var i = 0; i < $scope.timer.length; i++) {
        if ($scope.timer[i] !== undefined) {
          console.log("clear timer " + i.toString());
          $timeout.cancel($scope.timer[i]);
        }
      }
    };

    $scope.$on('$destroy', function (event) {
      console.log('clear timers');
      clearTimers();
    });


  }
]);
