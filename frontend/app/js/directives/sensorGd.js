angular.module('app').directive('sensorGd', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/sensor-gd.html',
    scope: {
      caption: '@',
      widgetHeight: '=?',
      value: '=',
      metadata: '=?'
    },

    link: function(scope) {
      // scope.ds = {};
      scope.type = "other";
      METADATA_TYPES = ["temperature", "humidity"];

      function updateValue(newValue) {

      }

      function init() {

        if (scope.metadata) {
          for (var i = 0; i < METADATA_TYPES.length; i++) {
            if (scope.metadata.type === METADATA_TYPES[i]) {
              scope.type = scope.metadata.type;
              break;
            }
          }
        }

        if (scope.widgetHeight === undefined) {
          scope.widgetHeight = 150;
        }

        scope.widgetWidth = 100;

        updateValue();
      }
      init();
      // scope.$watch('value', function(newValue, oldValue) {
      //   // if (newValue !== oldValue) {
      //   //   updateValue(newValue);
      //   // }else{
      //   //   console.log('no new data');
      //   // }
      //
      //   updateValue(newValue);
      // });

    }

  };
});
