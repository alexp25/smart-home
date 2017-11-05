angular.module('app').directive('sensorGdObj', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/sensor-gd-obj.html',
    scope: {
      caption: '@',
      widgetHeight: '=?',
      object: '=',
      graphic: '=?',
      metadata: '=?'
    },

    link: function(scope) {

      function init() {

      }
      init();


    }

  };
});
