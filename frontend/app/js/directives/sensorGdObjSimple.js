angular.module('app').directive('sensorGdObjSimple', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/sensor-gd-obj-simple.html',
    scope: {
      caption: '@',
      widgetHeight: '=?',
      object: '=',
      graphic: '=?',
      debug: '=?'
    },

    link: function(scope) {

      function init() {

      }
      init();


    }

  };
});
