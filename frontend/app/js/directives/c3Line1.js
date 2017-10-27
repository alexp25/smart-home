angular.module('app').directive('c3Line1', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/c3-line-1.html',
    scope: {
      data: '=',
      options: '=?',
      update: '=',
      cid: '=?'
    },
    link: function(scope) {
      if (scope.options === undefined) {
        scope.options = {
          cid: 1,
          height: 300,
          xtype: 'default',
          type: "spline",
          ymin: undefined,
          ymax: undefined,
          fullDate: false,
          showPoint: false,
          yminspan: undefined
        };
      } else {
        if (scope.options.showPoint === undefined) {
          scope.options.showPoint = false;
        }
      }



      if (scope.cid !== undefined) {
        scope.options.cid = scope.cid;
      }

      scope.rows1 = [];

      var containerid = "container-" + scope.options.cid.toString();
      $("#container").prop('id', containerid);
      var chartid = "chart-" + scope.options.cid.toString();
      $("#chart").prop('id', chartid);
      var height = $("#" + containerid).height();
      var width = $("#" + containerid).width();

      var timeCrt = new Date();

      function pad(str, max) {
        return str.length < max ? pad("0" + str, max) : str;
      }

      var chartdata = {
        bindto: '#' + chartid,
        size: {
          height: scope.options.height,
          width: scope.options.width
        },
        transition: {
          duration: 0
        },
        data: {
          labels: false,

          // line
          // spline
          // step
          // area
          // area-spline
          // area-step
          // bar
          // scatter
          // pie
          // donut
          // gauge

          type: scope.options.type,
          x: 'x',
          // xFormat: '%Y%m%d', // 'xFormat' can be used as custom format of 'x'
          // columns: [
          //   ['x', '2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04', '2013-01-05', '2013-01-06'],
          //   //            ['x', '20130101', '20130102', '20130103', '20130104', '20130105', '20130106'],
          //   ['data1', 30, 200, 100, 400, 150, 250],
          //   ['data2', 130, 340, 200, 500, 250, 350]
          // ],
          rows: [
            // ['x', 'data2', 'data3'],
            // [timeCrt, 0, 0],
          ]
        },
        padding: {
          top: 20
        },
        axis: {
          x: {
            tick: {
              count: 10,
              // format: function(x) {
              //   return Math.floor(x);
              // }
              // culling: true,
              // culling: {
              //   max: 4 // the number of tick texts will be adjusted to less than this value
              // }
            }
          },
          y: {
            max: scope.options.ymax,
            min: scope.options.ymin,

            // tick: {
            //   count: 10,
            //   format: function(x) {
            //     return Math.floor(x);
            //   }
            // }
          }
        },
        point: {
          show: scope.options.showPoint
        },
        grid: {
          x: {
            show: false
          },
          y: {
            show: true
          }
        },
        legend: {
          show: true
        },
        tooltip: {
          show: true
        },
        zoom: {
          enabled: true
        },
        onresize: function() {
          console.log("resized");
          // chart.resize();

          // var size = {
          //   height: $('#parentContainer')[0].offsetHeight - 10
          // }
          // chart.resize(size);
          // var width = $('#' + containerid).width();
          // console.log(width);
          //
          // chart.resize({
          //   width: width
          // });
        }
      };


      if (scope.options.xtype === 'timeseries') {
        chartdata.axis.x.type = "timeseries";
        chartdata.axis.x.tick.format = '%H:%M:%S';
      }
      if (scope.options.format) {
        chartdata.axis.x.tick.format = scope.options.format;
        // chartdata.axis.x.tick.format = '%Y-%m-%d %H:%M:%S';
      } else {
        // chartdata.axis.x.tick.format = '%H:%M:%S';
        chartdata.axis.x.tick.format = function(x) {
          return pad(x.getHours().toString(), 2) + ":" + pad(x.getMinutes().toString(), 2) + ":" + pad(x.getSeconds().toString(), 2) + "." +
            pad(x.getMilliseconds().toString(), 3);
        };
        // format: function (x) { return x.getFullYear(); }
      }

      var chart = c3.generate(chartdata);

      console.log("chart loaded");


      function addToChart(value, rows, n, caption) {
        timeCrt = new Date();
        if (rows.length === 0) {
          rows.push(['x', caption]);
        }
        // it does not work if data is undefined (errors)
        if (value === undefined) {
          value = 0;
        }

        if (rows.length >= n) {
          rows.splice(1, 1);
          rows.push([timeCrt, value]);
        } else {
          rows.push([timeCrt, value]);
        }

        return rows;
      }

      function updateChart(data) {
        // chartdata.data.rows.unshift(data.columns);
        // if (data.refresh) {
        //   chart.unload();
        // }



        rows1 = addToChart(data, scope.rows1, 50, scope.options.caption);
        // console.log(rows1);
        // var rows1 = [
        //   ['x', 'data'],
        //   [timeCrt, data],
        //   // [2, 160, 240],
        //   // [3, 200, 290],
        //   // [4, 160, 230],
        //   // [5, 130, 300],
        //   // [6, 220, 320]
        // ]

        chart.load({
          rows: rows1
        });
      }



      scope.$watch('update', function() {
        if (chartdata !== undefined && scope.data !== undefined) {
          updateChart(scope.data);
        }
      });

    }
  };
});
