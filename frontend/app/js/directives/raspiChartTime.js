angular.module('app').directive('raspiChartTime', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/raspi-chart-time.html',
    scope: {
      caption: '@',
      array: '=',
      update: '=?',
      size: '=?',
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
        if (!scope.size) {
          scope.size = {};
          scope.size.width = 400;
          scope.size.height = 300;
        }
        if (!scope.options) {
          scope.options = [];
          scope.options.xAxisType = 'numeric';
          scope.options.xAxisTickInterval = 10;
          scope.options.yAxisTickInterval = 10;
          scope.options.labels = ['chart', true];
          scope.options.minThreshold = 0;
          scope.options.maxThreshold = 0;

          /*scope.options.visible = [];
          for (i1 = 0; i1 < scope.array.length; i1 = i1 + 1) {
            scope.options.visible[i1] = true;
          }*/

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

        }
        var COLOR_DARK = '#263238';

        var height= $("#container").height();
        var width= $("#container").width();
        scope.chartConfig = {

          chart: {
            type: 'spline',
            zoomType: 'x',
            animation: {
              duration: 200,
              easing: "swing"
            },
            // Edit chart spacing
            spacingBottom: 15,
            spacingTop: 10,
            spacingLeft: 10,
            spacingRight: 10,

            // Explicitly tell the width and height of a chart
            width: width,
            height: height,
            events: {
              load: function(event) {
                setTimeout(function() {
                  console.log("chart reflow");
                  event.target.reflow();
                  console.log(width);
                  console.log(height);
                }, 0);
              }
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
            enabled: true
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
            },
            //tickInterval: 10*60*1000
            tickPixelInterval: 100
          },
          yAxis: {
            title: {
              text: ''
            },

            // plotLines: [{
            //   id: 'limit-min',
            //   color: '#FF0000',
            //   //dashStyle: 'ShortDash',
            //   width: 1,
            //   value: scope.options.minThreshold,
            //   zIndex: 0
            // }, {
            //   id: 'limit-max',
            //   color: '#FF0000',
            //   dashStyle: 'ShortDash',
            //   width: 1,
            //   value: scope.options.maxThreshold,
            //   zIndex: 0
            // }, {
            //   value: 0,
            //   width: 1,
            //   color: '#808080'
            // }],
            labels: {
              style: {
                color: COLOR_DARK,
                fontWeight: 'normal',
                fontSize: '15px'
              }
            },

            min: scope.options.range[0],
            max: scope.options.range[1],
            tickInterval: 100,
            gridLineColor: 'grey',
            gridLineWidth: 0,
            // gridLineWidth: 1,
            // gridLineDashStyle: 'longdash'
            gridLineDashStyle: 'solid'
          },
          tooltip: {
            valueSuffix: ''
          },

          legend: {
            enabled: false,
            align: 'right',
            backgroundColor: '#FCFFC5',
            borderColor: 'black',
            borderWidth: 2,
            layout: 'vertical',
            verticalAlign: 'top',
            y: 100,
            shadow: true
          },

          series: [{
            name: 'graph 1',
            data: []

          }, {
            name: 'graph 2',
            data: []
          }],
          //useHighStocks: true, //NAVIGATION BAR
          //size (optional) if left out the chart will default to size of the div or something sensible.
          // size: {
          //     width: 200
          //   //height: scope.size.height
          // },
          loading: false
        };


        scope.chartConfig.series = [];
        //  updateChart();

        scope.isLoaded = true;
      }

      function updateChart(array) {

        scope.chartConfig.yAxis.min = scope.options.range[0];
        scope.chartConfig.yAxis.max = scope.options.range[1];

        //scope.chartConfig.yAxis.tickInterval = Math.floor((scope.chartConfig.yAxis.max - scope.chartConfig.yAxis.min) / 5);
        //scope.chartConfig.xAxis.tickInterval = Math.floor(scope.array[0].length/10);
        //console.log(scope.chartConfig.xAxis.tickInterval);

        for (var i = 0; i < scope.array.length; i++) {
          if (i >= scope.chartConfig.series.length) {
            scope.chartConfig.series[i] = {};
          }
          scope.chartConfig.series[i].data = scope.array[i];
          scope.chartConfig.series[i].name = scope.options.labels[i].name;
          scope.chartConfig.series[i].visible = scope.options.labels[i].visible;
          scope.chartConfig.series[i].showInLegend = true;
          scope.chartConfig.series[i].lineWidth = 1;
          //scope.chartConfig.series[i].type = 'spline';
          scope.chartConfig.series[i].negativeColor = '#0088FF';

          if (scope.options.pointStart && scope.options.pointInterval) {
            scope.chartConfig.series[i].pointStart = scope.options.pointStart;
            scope.chartConfig.series[i].pointInterval = scope.options.pointInterval; // one day
            //console.log("chart pointStart: ", scope.options.pointStart);
          }
        }

        scope.chartConfig.series[0].color = '#005990';
      }

      init();

      scope.$watch('update', function() {
        //used for updating entire chart; including x axis
        console.log('update charts');
        if (scope.array !== undefined) {
          updateChart(scope.array);
        }
      });



    }

  };
});
