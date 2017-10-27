angular.module("app").factory('PollingService', ['$http', '$q', function($http, $q) {
  return {
    poll: function(api) {
      var deferred = $q.defer();
      $http.get(api).then(function(response) {
        deferred.resolve(response.data);
      }, function(response) {
        deferred.reject('ERROR');
      });
      return {
        promise: deferred.promise,
        abort: function() {
          deferred.reject('Aborted');
        }
      };
    },
    pollPost: function(api) {
      var deferred = $q.defer();
      $http.post(api).then(function(response) {
        deferred.resolve(response.data);
      });
      return {
        promise: deferred.promise,

        abort: function() {
          deferred.reject('Aborted');
        }
      };
    }

  };
}]);
