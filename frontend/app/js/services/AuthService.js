angular.module('app').service('AuthService', ['$q', '$timeout', '$http', '$cookies', 'SharedProperties', 'GlobalFcnService',
  function($q, $timeout, $http, $cookies, SharedProperties, GlobalFcnService) {
    //to create unique contact id
    // create user variable
    var user = false;

    this.isLoggedInCheck = function() {
      return user;
    };



    this.isLoggedInCheckServer = function() {

      //var username = $cookies.get('username');
      // send a post request to the server
      var url = SharedProperties.getOneProperty("url");
      var deferred = $q.defer();
      $http.get(url + '/api/isloggedin')
        // handle success
        .then(function(data) {
          console.log(data);
          if (data.status === 200 && data.data.result === SharedProperties.getOneProperty("constants").RESULT_OK) {
            user = true;
            console.log('ok');

            GlobalFcnService.requestAndSaveAppSettings();

            deferred.resolve();
          } else {
            user = false;
            deferred.reject();
          }
        })
        // handle error
        .catch(function(data) {
          user = false;
          deferred.reject();
        });

      // return promise object
      return deferred.promise;


    };

    this.login = function(username, password) {

      // create a new instance of deferred
      var deferred = $q.defer();
      var url = SharedProperties.getOneProperty("url");

      $http.post(url + '/api/login', {
          username: username,
          password: password
        })
        // handle success
        .then(function(data) {
          //console.log(data);
          if (data.status === 200 && data.data.result === SharedProperties.getOneProperty("constants").RESULT_OK) {
            user = true;
            //console.log('ok');
            deferred.resolve();
          } else {
            user = false;
            deferred.reject();
          }
        })
        // handle error
        .catch(function(data) {
          user = false;
          deferred.reject();
        });

      // return promise object
      return deferred.promise;

    };

    this.logout = function() {

      // create a new instance of deferred
      var deferred = $q.defer();
      var url = SharedProperties.getOneProperty("url");

      // send a get request to the server
      $http.get(url + '/api/logout')
        // handle success
        .then(function(data) {
          user = false;
          deferred.resolve();
        })
        // handle error
        .catch(function(data) {
          user = false;
          deferred.reject();
        });

      // return promise object
      return deferred.promise;

    };

    this.register = function(userdata) {

      // create a new instance of deferred
      var deferred = $q.defer();
      var url = SharedProperties.getOneProperty("url");

      // send a post request to the server
      $http.post(url + '/api/register',
          userdata
        )
        // handle success
        .then(function(data) {
          if (data.status === 200 && data.data.result === SharedProperties.getOneProperty("constants").RESULT_OK) {
            deferred.resolve();
          } else {
            deferred.reject();
          }
        })
        // handle error
        .catch(function(data) {
          deferred.reject();
        });

      // return promise object
      return deferred.promise;

    };

  }
]);
