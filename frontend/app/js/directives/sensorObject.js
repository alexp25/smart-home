angular.module('app').directive('sensorObject', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/sensor-object.html',
    scope: {
      caption: '@',
      debug: "=?",
      graphic: '=?',
      widgetHeight: '=?',
      object: '='
    },

    link: function(scope) {
      // scope.ds = {};
      function updateValue(newValue) {
        var aux;
        aux = newValue;
        if (aux > scope.object.maxValue) {
          aux = scope.object.maxValue;
        }
        if (aux < scope.object.minValue) {
          aux = scope.object.minValue;
        }

        if (!isNaN(aux)) {
          scope.value = aux;
          scope.validData = true;
        } else {
          scope.value = scope.object.minValue;
        }
      }

      function init() {
        scope.validData = false;
        scope.type = 'other';
        if (scope.object.type !== '') {
          scope.type = scope.object.type;
        }

        if (scope.widgetHeight === undefined) {
          scope.widgetHeight = 150;
        }

        scope.widgetWidth = 100;

        updateValue();
      }
      init();
      scope.$watch('object.value', function(newValue, oldValue) {
        // if (newValue !== oldValue) {
        //   updateValue(newValue);
        // }else{
        //   console.log('no new data');
        // }
        updateValue(newValue);
      });

    }

  };
});
