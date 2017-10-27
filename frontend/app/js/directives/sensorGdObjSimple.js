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
      /**
      This directive receives the data and metadata for a node
      object: array
      metadata: array of metadata objects
      */

      // scope.ds = {};
      METADATA_TYPES = ["temperature", "humidity"];

      function updateValue(newValue) {

      }

      function init() {
        // scope.type = "other";
        // for (var i = 0; i < METADATA_TYPES.length; i++) {
        //   if (metadata.type === METADATA_TYPES[i]) {
        //     scope.type = metadata.type;
        //     break;
        //   }
        // }


        updateValue();
      }
      init();
      // scope.$watch('object.value', function(newValue, oldValue) {
      //   // if (newValue !== oldValue) {
      //   //   updateValue(newValue);
      //   // }else{
      //   //   console.log('no new data');
      //   // }
      //   updateValue(newValue);
      // });

    }

  };
});
