angular.module('app').controller('wsProgramCtrl', ['SharedProperties', '$scope',
  '$log', '$timeout', '$filter', '$http',
  function(SharedProperties, $scope, $log, $timeout, $filter, $http) {
    $scope.isLoaded = false;
    $scope.currentFocused = "";

    $scope.gridOptions = {
      columnDefs: [{
        name: 'id',
        field: 'index',
        enableCellEdit: false,
        width: 100
      }, {
        name: 'position',
        field: 'dist',
        type: 'number',
        headerCellClass: 'blue'

      }, {
        name: 'time',
        field: 'time',
        type: 'number',
        headerCellClass: 'white'

      }],
      data: [],
      importerDataAddCallback: function(grid, newObjects) {
        $scope.gridOptions.data = newObjects;
      },
      onRegisterApi: function(gridApi) {
        $scope.gridApi = gridApi;
      }
    };

    $scope.program = {
      interval: {
        h: 12,
        m: 0,
        s: 0
      }
    };

    $scope.randomSize = function() {
      var newHeight = Math.floor(Math.random() * (300 - 100 + 1) + 300);
      var newWidth = Math.floor(Math.random() * (600 - 200 + 1) + 200);

      angular.element(document.getElementsByClassName('grid')[0]).css('height', newHeight +
        'px');
      angular.element(document.getElementsByClassName('grid')[0]).css('width', newWidth +
        'px');
    };

    $scope.addData = function() {
      var n = $scope.gridOptions.data.length;
      $scope.gridOptions.data.push({
        "index": n,
        "dist": undefined,
        "time": undefined
      });
    };

    $scope.removeSelectedRow = function() {
      //if($scope.gridOpts.data.length > 0){
      var rowCol = $scope.gridApi.cellNav.getFocusedCell();
      if (rowCol !== null) {
        $scope.currentFocused = 'Row Id:' + rowCol.row.entity.index + ' col:' + rowCol.col.colDef
          .name;
        $scope.gridOptions.data.splice(rowCol.row.entity.index, 1);
      }
      reindex();
    };

    var reindex = function() {
      for (var i = 0; i < $scope.gridOptions.data.length; i++) {
        $scope.gridOptions.data[i].index = i;
      }
    };

    $scope.getCurrentFocus = function() {
      var rowCol = $scope.gridApi.cellNav.getFocusedCell();
      if (rowCol !== null) {
        $scope.currentFocused = 'Row Id:' + rowCol.row.entity.index + ' col:' + rowCol.col.colDef
          .name;
      }
    };

    var getTotal = function(vec, prop) {
      var sum = 0;
      var i = 0;
      if (prop) {
        for (i = 0; i < vec.length; i++) {
          sum = sum + vec[i][prop];
        }
      } else {
        for (i = 0; i < vec.length; i++) {
          sum = sum + vec[i];
        }
      }
      return sum;
    };

    $scope.updateTotal = function() {
      console.log('total updata for: ', $scope.currentProgram.data);
      $scope.currentProgram.total = getTotal($scope.currentProgram.data, 'time');
    };

    $scope.requestProgram = function() {
      $scope.hasData = false;
      console.log('requestProgram');
      $http.get($scope.serverURL + '/api/ws/program').
      then(function(data) {
        // this callback will be called asynchronously
        // when the response is available
        $scope.jsondata = angular.toJson(data.data);
        var jsonObj = angular.fromJson(data.data);
        console.log(jsonObj);
        $scope.currentProgram.data = jsonObj.program;
        $scope.gridOptions.data = jsonObj.program;
        $scope.program.interval = jsonObj.interval;
        //SharedProperties.getProperty().gridOptions.data = $scope.gridOptions.data;
        $scope.updateTotal();
        //console.log($scope.currentProgram);

        $scope.infoList = [{
          name: 'total watering time',
          value: $scope.currentProgram.total
        }, {
          name: 'positions',
          value: $scope.currentProgram.data.length
        }];
        $scope.hasData = true;
      }).
      catch(function(data) {
        // called asynchronously if an error occurs
        // or server returns response with an error status.
        $scope.jsondata = 'error';
        $scope.hasData = true;
      //  alert('error');
      });
    };

    $scope.updateProgram = function() {
      var filled = true,
        number = true;
      angular.forEach($scope.gridOptions.data, function(value, key) {
        angular.forEach(value, function(value, key) {
          if (key !== '$$hashKey') {
            if (value === undefined && filled) {
              alert('Fill in the required field: ' + key);
              filled = false;
            } else if (angular.isString(value) && number) {
              alert('Enter a valid number in the required field: ' + key);
              number = false;
            }
          }
          console.log(key, ' ', value);
        });
      });

      if (!(filled && number)) {
        console.log('Fill in the required fields');
        return;
      }
      $scope.hasData = false;
      $http.post($scope.serverURL + '/api/ws/program', {
        'program': $scope.gridOptions.data,
        'interval': $scope.program.interval
      }).
      then(function(data) {
        console.log('post success');
        $scope.hasData = true;
      }).
      catch(function(data) {
        console.log('post error');
        $scope.hasData = true;
        //alert('error');
      });
    };

    $scope.init = function() {
      //$scope.fullContentHeight = SharedProperties.getProperty().documentSettings.fullContentHeight;
      var props = SharedProperties.getProperty();
      $scope.serverURL = props.url;
      $scope.currentProgram = {};
      $scope.currentProgram.data = props.ws.settings.program;
      $scope.updateTotal();

      angular.merge($scope.gridOptions, props.gridOptions);
      $scope.gridOptions.data = $scope.currentProgram.data;

      $scope.requestProgram();
      $scope.isLoaded = true;
    };

  }
]);
