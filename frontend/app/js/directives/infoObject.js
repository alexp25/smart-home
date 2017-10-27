angular.module('app').directive('infoObject', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/info-object.html',
    scope: {
      caption: '@',
      object: '='
    },
    link: function(scope) {
      function init() {
        // console.log("object");
        // console.log(scope.object);
      }
      init();
    }

  };
});
