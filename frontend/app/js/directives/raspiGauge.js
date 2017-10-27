angular.module('app').directive('raspiGauge', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/raspi-gauge.html',
    scope: {
      caption: '@',
      value: '=',
      range: '=?',
      size: '=?',
      angle: '=?',
      datalabels: '=?'
    },
    link: function(scope) {

      function init() {
        scope.isLoaded = false;
        // console.log(scope);
        if (!scope.range) {
          scope.range = [0, 100];
        }
        if (scope.value === undefined) {
          scope.value = 0;
        }
        if (!scope.size) {
          scope.size = {};
          //scope.size.width = undefined;
          scope.size.height = 200;
        }
        if (!scope.caption) {
          scope.caption = '';
        }

        scope.labelX = 40;
        scope.labelY = 0;
        scope.center = ['50%', '85%'];
        scope.paneSize = '150%';
        scope.reversed = false;

        if (!scope.angle) {
          scope.angle = [-90, 90];
        } else {
          /*scope.center = ['50%', '50%'];
          scope.paneSize = '100%';*/
        }

        scope.chartConfig = {
          options: {
            chart: {
              type: 'gauge',
              animation: {
                duration: 100,
                easing: "swing"
              }
            },
            pane: {
              center: scope.center,
              size: scope.paneSize,
              startAngle: scope.angle[0],
              endAngle: scope.angle[1],
              background: {
                backgroundColor: '#263238',
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
              }
            }
          },
          series: [{
            name: scope.caption,
            data: [scope.value],
            dial: {
              radius: '100%',
              backgroundColor: 'silver',
              borderColor: 'black',
              borderWidth: 1,
              baseWidth: 10,
              topWidth: 1,
              baseLength: '90%', // of radius
              rearLength: '10%'
            },


            dataLabels: {
              enabled: scope.datalabels,
              formatter: function() {
                var kmh = this.y;
                return '<span>' + kmh + '</span><br/>';
              },
              style: {
                //  color: '#BBB',
                fontStyle: 'italic',
                fontWeight: 'normal',
                fontSize: '24px',
                lineHeight: '10px'
              },
              y: scope.labelX,
              x: scope.labelY,
              backgroundColor: {
                linearGradient: {
                  x1: 0,
                  y1: 0,
                  x2: 0,
                  y2: 1
                },
                stops: [
                  [0, '#DDD'],
                  [1, '#FFF']
                ]
              }
            },
            animation: {
              duration: 500,
              easing: "easeOutBounce"
            }
          }],
          title: {
            text: '',
            y: 100
          },

          xAxis: {

          },

          yAxis: {
            currentMin: scope.range[0],
            currentMax: scope.range[1],
            reversed: scope.reversed,

            plotBands: [{
              from: scope.range[0],
              to: 0,
              color: '#FFF3E0'
            }, {
              from: 0,
              to: scope.range[1],
              color: '#FF9800'
            }],

            lineWidth: 10,
            tickInterval: 50,
            //tickInterval: (scope.range[1] - scope.range[0]) / 3,
            tickPixelInterval: 400,
            tickWidth: 0,

            loading: false,
            useHighStocks: false
          },
          size: {
            width: scope.size.width,
            height: scope.size.height
          }

        };

        scope.isLoaded = true;
      }

      function updateChart(val) {
        scope.chartConfig.series[0].data = [val];
        //scope.chartConfig.title.text = scope.caption;
      }

      scope.$watch('value', function(newValue, oldValue) {
        if (newValue !== oldValue) {
          updateChart(newValue);
        }
      });

      init();
    }

  };
});
