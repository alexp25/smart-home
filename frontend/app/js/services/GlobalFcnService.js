angular.module("app").factory('GlobalFcnService', ['$q', '$http', 'SharedProperties', function($q, $http, SharedProperties) {
  var fcn = {};
  fcn.chunk = function(arr, size) {
    var newArr = [];
    for (var i = 0; i < arr.length; i += size) {
      newArr.push(arr.slice(i, i + size));
    }
    return newArr;
  };
  fcn.getCookie = function(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "alex";
  };
  fcn.getSettings = function() {
    var user = fcn.getCookie("username");
    var url = SharedProperties.getProperty().url;
    var promise = $http.get(url + '/api/database/settings', {
      params: {
        username: user
      }
    });
    return promise;
  };

  fcn.getGeneralSettings = function() {
    var user = fcn.getCookie("username");
    var url = SharedProperties.getProperty().url;
    var promise = $http.get(url + '/api/general/settings');
    return promise;
  };

  fcn.requestAndSaveAppSettings = function() {
    fcn.getSettings().then(function(response) {
      n = response.data;
      SharedProperties.setOneProperty("userSettings", n);

      // var wsurl = n.userSettings.app.ws_url;
      // if (wsurl === 'localhost') {
      //   wsurl = 'ws://' + document.location.host;
      // }
      // SharedProperties.setOneProperty("wsurl", wsurl);
    }, function(err) {
      alert('error getting app settings');
    });
  };



  fcn.postSettings = function(data) {
    var user = fcn.getCookie("username");
    var url = SharedProperties.getProperty().url;
    $http.post(url + '/api/database/settings', {
      'username': user,
      'settings': data
    }).
    then(function(data, status, headers, config) {
        console.log('post settings success');
      })
      .catch(function(data, status, headers, config) {
        console.log('post settings error');
      });
  };

  return fcn;

}]);
