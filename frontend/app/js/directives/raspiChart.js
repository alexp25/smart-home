angular.module('app').directive('raspiChart', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/raspi-chart.html',
    scope: {
      caption: '@',
      array: '=',
      update: '=',
      frame: '=?',
      options: '='
    },
    link: function(scope) {
      function init() {

        var i1;

        if (!scope.array) {
          scope.array = [];
        }
        if (!scope.labels) {
          scope.labels = [];
        }

        if (!scope.options) {
          scope.options = [];
          scope.options.xAxisType = 'numeric';
          scope.options.xAxisTickInterval = 10;
          scope.options.yAxisTickInterval = 10;
          scope.options.labels = ['chart'];

          scope.options.visible = [];
          for (i1 = 0; i1 < scope.array.length; i1 = i1 + 1) {
            scope.options.visible[i1] = true;
          }

        } else {
          //console.log(scope.options);
          if (scope.options.range === undefined) {
            scope.options.range = [];
          }


          //scope.options.xRange = [new Date('2000/10/22').getTime(), new Date('2000/10/23').getTime()];

          if (!scope.options.xAxisTickInterval) {
            scope.options.xAxisTickInterval = 10;
          }
          if (!scope.options.yAxisTickInterval) {
            scope.options.yAxisTickInterval = 10;
          }
          if (!scope.options.visible) {
            scope.options.visible = [];
            for (i1 = 0; i1 < scope.array.length; i1 = i1 + 1) {
              scope.options.visible[i1] = true;
            }
          }
        }
        var COLOR_DARK = '#263238';

        scope.chartConfig = {

          chart: {
            type: 'area',
            zoomType: 'x',
            animation: {
              duration: 10,
              easing: "swing"
            }
          },
          plotOptions: {
            line: {
              marker: {
                enabled: false
              }
            },
            spline: {
              marker: {
                enabled: false
              }
              // ,
              // dataLabels: {
              //   enabled: true
              // }
            },
            area: {
              marker: {
                enabled: false
              }
            }
          },

          navigator: {
            enabled: false
          },
          exporting: {
            enabled: false
          },

          title: {
            text: '',
            x: -20 //center
          },
          subtitle: {
            text: '',
            x: -20
          },
          xAxis: {
            type: scope.options.xAxisType,
            labels: {
              style: {
                color: COLOR_DARK,
                fontWeight: 'normal',
                fontSize: '15px'
              }
            }
          },
          yAxis: {
            title: {
              text: ''
            },
            plotLines: [{
              value: 0,
              width: 1,
              color: '#808080'
            }],
            labels: {
              style: {
                color: COLOR_DARK,
                fontWeight: 'normal',
                fontSize: '15px'
              }
            },
            min: scope.options.range[0],
            max: scope.options.range[1],
            tickInterval: scope.options.yAxisTickInterval,
            gridLineColor: COLOR_DARK,
            gridLineWidth: 0,
            gridLineDashStyle: 'solid'
          },
          tooltip: {
            valueSuffix: ''
          },
          legend: {
            layout: 'vertical',
            align: 'bottom',
            verticalAlign: 'middle',
            borderWidth: 0
          },
          series: [{
            name: 'graph 1',
            data: []

          }, {
            name: 'graph 2',
            data: []
          }],
          useHighStocks: false
            //size (optional) if left out the chart will default to size of the div or something sensible.
          // size: {
          //   width: 200
          //   //height: scope.size.height
          // }
        };


        scope.chartConfig.series = [];
        //  updateChart();

        scope.isLoaded = true;
      }

      function updateChart(array) {
        /*scope.chartConfig.series[0].data = array[0];
        scope.chartConfig.series[1].data = array[1];*/
        /*for (var i = 0; i < scope.array.length; i++) {
          scope.chartConfig.series[i].data = scope.array[i];
        }*/
        /*  if (scope.options.xRange !== undefined) {
            scope.chartConfig.xAxis.min = scope.options.xRange[0];
            scope.chartConfig.xAxis.max = scope.options.xRange[1];
          }*/

        for (var i = 0; i < scope.array.length; i++) {
          if (i >= scope.chartConfig.series.length) {
            scope.chartConfig.series[i] = {};
          }
          scope.chartConfig.series[i].data = scope.array[i];
          scope.chartConfig.series[i].lineWidth = 1;
          /*  var s = new Date();
            var dt;
            scope.chartConfig.series[i].data = {};
            for (var j = 0; j < scope.array[i].length; j++) {

              dt = s.getDate();
              dt = new Date(s.setDate(dt+1));
              console.log(dt);
              scope.chartConfig.series[i].data[j] = [dt, scope.array[i][j]];
            }*/
          scope.chartConfig.series[i].name = scope.options.labels[i];
          scope.chartConfig.series[i].visible = scope.options.visible[i];

          if (scope.options.pointStart && scope.options.pointInterval) {
            scope.chartConfig.series[i].pointStart = scope.options.pointStart;
            scope.chartConfig.series[i].pointInterval = scope.options.pointInterval; // one day
            //console.log("chart pointStart: ", scope.options.pointStart);
          }
        }

      }

      init();

      scope.$watch('update', function() {
        //used for updating entire chart; including x axis
        //console.log('update charts');
        // console.log('update');
        if (scope.array !== undefined) {
          updateChart(scope.array);
        }
      });



    }

  };
});
