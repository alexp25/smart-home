angular.module('app').filter('secondsToDateTime', function() {
  return function(seconds) {
    var d = new Date(0, 0, 0, 0, 0, 0, 0);
    d.setSeconds(seconds);
    return d;
  };
});

angular.module('app').filter('zpad', function() {
  return function(input, n) {
    var zeros = "";
    var inp;
    if (input === undefined) {
      input = "";
    }
    /*if (input.length >= n) {
        return input;
    }*/
    if (input < 0) {
      input = -input;
      zeros = "0".repeat(n);
      return "-" + (zeros + input).slice(-1 * n);
    } else {
      zeros = "0".repeat(n);
      return " " + (zeros + input).slice(-1 * n);
    }
  };
});

angular.module("app").filter("sanitize", ['$sce', function($sce) {
  return function(htmlCode) {
    return $sce.trustAsHtml(htmlCode);
  };
}]);
