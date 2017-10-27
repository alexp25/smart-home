// create a new factory
angular.module('app').factory('StorageService', function($localStorage) {

  $localStorage = $localStorage.$default({
    things: [],
    data: undefined
  });

  var _getAll = function() {
    return $localStorage.things;
  };
  var _add = function(thing) {
    $localStorage.things.push(thing);
  };
  var _remove = function(thing) {
    $localStorage.things.splice($localStorage.things.indexOf(thing), 1);
  };
  var _getData = function() {
    return $localStorage.data;
  };
  var _setData = function(data) {
    $localStorage.data = data;
  };
  return {
    getAll: _getAll,
    add: _add,
    remove: _remove,
    getData: _getData,
    setData: _setData
  };
});
