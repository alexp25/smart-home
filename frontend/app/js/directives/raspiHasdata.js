angular.module('app').directive('raspiHasdata', function(){
    return{
        restrict: 'E',
        templateUrl: 'templates/directives/raspi-hasdata.html',
        scope: {
            hasData: '='
        },
        link: function (scope) {
            /*scope.items= [
                    { name: 'Item 1', value: 'Url1' },
                    { name: 'Item 2', value: 'Url2' }
            ];*/
        }

    };
});
