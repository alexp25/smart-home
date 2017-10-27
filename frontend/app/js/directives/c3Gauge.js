angular.module('app').directive('c3Gauge', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/c3-gauge.html',
    scope: {
      data: '=',
      options: '=?',
      cid: '=?'
    },
    link: function(scope) {

      if (scope.options === undefined) {
        scope.options = {
          cid: 1,
          height: 120,
          width: 180,
          ymin: 0,
          ymax: 100,
          caption: 'gauge',
          unit: ''
        };
      }
      if (scope.cid !== undefined) {
        scope.options.cid = scope.cid;
      }

      var containerid = "container-" + scope.options.cid.toString();
      $("#container").prop('id', containerid);
      var chartid = "chart-" + scope.options.cid.toString();
      $("#chart").prop('id', chartid);
      var height = $("#" + containerid).height();
      var width = $("#" + containerid).width();

      var chartdata = {
        bindto: '#' + chartid,
        size: {
          height: scope.options.height
        },
        transition: {
          duration: 0
        },
        data: {
          columns: [
            ['data', -1]
          ],
          type: 'gauge',
          onclick: function(d, i) {
            console.log("onclick", d, i);
          },
          onmouseover: function(d, i) {
            console.log("onmouseover", d, i);
          },
          onmouseout: function(d, i) {
            console.log("onmouseout", d, i);
          }
        },
        // padding: {
        //   bottom: 20
        // },
        gauge: {
          label: {
            format: function(value, ratio) {
              return value.toString() + " " + scope.options.unit;

            },
            show: true // to turn off the min/max labels.
          },
          min: scope.options.ymin, // 0 is default, //can handle negative min e.g. vacuum / voltage / current flow / rate of change
          max: scope.options.ymax, // 100 is default
          units: '',
          width: 39 // for adjusting arc thickness
        },
        title: {
          text: scope.options.caption
        },

        color: {
          // pattern: ['#FF0000', '#F97600', '#F6C600', '#60B044'], // the three color levels for the percentage values.
          pattern: ['#4A7EA6'],
          threshold: {
            //            unit: 'value', // percentage is default
            //            max: 200, // 100 is default
            // values: [30, 60, 90, 100]
            values: [0]
          }
        },
        tooltip: {
          show: false
        }
      };



      var chart = c3.generate(chartdata);

      var addTicks = function() {
        // add ticks (optional)
        var ticksValues = [0, 25, 50, 75, 100];

        var ticks = d3.select('.c3-chart-arcs')
          .append('g')
          .selectAll("line")
          .data(ticksValues).enter()
          .append("line")
          .attr("x1", 0)
          .attr("x2", 0)
          .attr("y1", -chart.internal.radius + 20)
          .attr("y2", -chart.internal.radius)
          .attr("transform", function(d) {
            var min = chart.internal.config.gauge_min,
              max = chart.internal.config.gauge_max,
              ratio = d / (max - min),
              rotate = (d - 2) * 45;
            return "rotate(" + rotate + ")";
          });
      };

      //addTicks();

      function updateChart(data) {
        var columns1 = [
          ['data', data]
        ];
        chart.load({
          columns: columns1
        });
        // console.log(columns1);
      }

      scope.$watch('data', function() {
        //used for updating entire chart; including x axis
        //console.log('update charts');
        // console.log(scope.data);
        if (chartdata !== undefined) {
          updateChart(scope.data);
        }
      });

    }
  };
});
