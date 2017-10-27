angular.module('app')
  .service('SharedProperties', ['uiGridConstants', function(uiGridConstants) {
    // .service('SharedProperties', function() {
    var property = {
      // url: "http://192.168.1.10:8000",
      // wsurl: "ws://192.168.1.10:8000",
      url: '',
      wsurl: 'ws://' + document.location.host,

      // webSocket = new WebSocket('ws://' + document.domain + ':' + $scope._port + '/app-data/server-main');
      //url: "localhost:",
      // url: '',
      port: 8000,
      userSettings: {},
      documentSettings: {
        fullContentHeightPromise: undefined,
        fullContentHeight: 0,
        showSidenav: true,
        mjpegStream: true,
        mobileVersion: false
      },
      constants: {
        MODE_AUTO: 0,
        MODE_MANUAL: 1,
        MODE_TEST: 2,
        RESULT_OK: 0,
        RESULT_FAIL: 1
      },
      ws: {
        settings: {
          mode: [{
            label: "auto",
            value: 0
          }, {
            label: "manual",
            value: 1
          }, {
            label: "test",
            value: 2
          }],
          updateRate: [{
            label: "standard",
            value: 0
          }, {
            label: "fast",
            value: 1
          }],
          program: [],
          trackLen: 25000,
          nextSq: {
            h: 12,
            m: 0
          },
          resetCountdown: true,
          maxPumpCommand: 200,
          Kp: 1,
          Ki: 0,
          Kd: 0
        }
      },
      gridOptions: {
        enableSorting: true,
        enableCellEditOnFocus: true,
        enableGridMenu: true,
        enableVerticalScrollbar: uiGridConstants.scrollbars.WHEN_NEEDED,
        enableHorizontalScrollbar: uiGridConstants.scrollbars.NEVER,

        exporterCsvFilename: 'myFile.csv',
        exporterCsvLinkElement: angular.element(document.querySelectorAll(
          ".custom-csv-link-location"))
      }
    };

    return {
      getProperty: function() {
        return property;
      },
      getOneProperty: function(field) {
        return property[field];
      },
      getDocSize: function() {
        return property.documentSettings.fullContentHeight;
      },
      setProperty: function(value) {
        property = value;
      },
      setOneProperty: function(field, value) {
        console.log("set " + field);
        console.log(value);
        property[field] = value;
      }
    };
  }]);
// });
