angular.module('app').directive('showTail', function () {
    return function (scope, elem, attr) {
        scope.$watch(function () {
            console.log("a");
            return elem[0].value;
 
        },
        function (e) {
            elem[0].scrollTop = elem[0].scrollHeight;
        });
    };
});
