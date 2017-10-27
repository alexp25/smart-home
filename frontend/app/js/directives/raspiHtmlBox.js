angular.module('app').directive('raspiHtmlBox', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/raspi-html-box.html',
    scope: {
      caption: '@',
      html: '='
    },
    link: function(scope) {}
  };
});
