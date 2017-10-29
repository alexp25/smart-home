/* Exports a function which returns an object that overrides the default &
 *   plugin file patterns (used widely through the app configuration)
 *
 * To see the default definitions for Lineman's file paths and globs, see:
 *
 *   - https://github.com/linemanjs/lineman/blob/master/config/files.coffee
 */
module.exports = function(lineman) {
  //Override file patterns here
  return {

    js: {
      vendor: [
        'vendor/bower_components/jquery/dist/jquery.js',
        //
        // 'vendor/bower_components/ionic/js/ionic.bundle.js',


        'vendor/bower_components/angular/angular.js',

        'vendor/bower_components/angular-bootstrap/ui-bootstrap.js',
        'vendor/bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
        'vendor/bower_components/angular-aria/angular-aria.js',
        'vendor/bower_components/angular-animate/angular-animate.js',
        'vendor/bower_components/angular-material/angular-material.js',
        'vendor/bower_components/angular-ui-router/release/angular-ui-router.js',
        'vendor/bower_components/angular-touch/angular-touch.js',
        'vendor/bower_components/angular-websocket/dist/angular-websocket.js',
        'vendor/bower_components/angular-sanitize/angular-sanitize.js',
        'vendor/bower_components/angularjs-slider/dist/rzslider.js',

        'vendor/bower_components/ng-csv/build/ng-csv.js',

        'vendor/bower_components/socket.io-client/socket.io.js',

        'vendor/bower_components/jquery-ui/jquery-ui.js',
        'vendor/bower_components/bootstrap/dist/js/bootstrap.js',

        'vendor/bower_components/bootstrap-switch/dist/js/bootstrap-switch.js',



        'vendor/bower_components/d3/d3.js',
        'vendor/bower_components/c3/c3.js',

        // 'vendor/bower_components/highcharts/highstock.src.js',
        // 'vendor/bower_components/highcharts/highcharts-more.src.js',
        'vendor/bower_components/highcharts/highstock.src.js',
        'vendor/bower_components/highcharts/highcharts-more.src.js',
        'vendor/bower_components/highcharts/modules/exporting.js',

        'vendor/bower_components/highcharts-ng/dist/highcharts-ng.js',

        // 'vendor/bower_components/highcharts/highcharts.src.js',

        // 'vendor/bower_components/highcharts-ng/dist/highcharts-ng.js',


        'vendor/bower_components/angular-animate/angular-animate.js',
        'vendor/bower_components/angular-cookies/angular-cookies.js',
        'vendor/bower_components/angular-ui/build/angular-ui.js',
        'vendor/bower_components/angular-ui-grid/ui-grid.js',

        'vendor/bower_components/angular-messages/angular-messages.js',

        'vendor/bower_components/angular-scroll-glue/src/scrollglue.js',

        'vendor/bower_components/use-form-error/dist/use-form-error.js',

        // 'vendor/bower_components/angular-local-storage/dist/angular-local-storage.js',

        'vendor/bower_components/ngstorage/ngStorage.js',

        // ngflowchart
        // 'vendor/bower_components/ngFlowchart/dist/ngFlowchart.js',
        // 'vendor/bower_components/ngFlowchart/dist/vendor.js',

        // 'vendor/libs/AngularJS-FlowChart/flowchart/svg_class.js',
        // 'vendor/libs/AngularJS-FlowChart/flowchart/mouse_capture_service.js',
        // 'vendor/libs/AngularJS-FlowChart/flowchart/dragging_service.js',
        // 'vendor/libs/AngularJS-FlowChart/flowchart/flowchart_viewmodel.js',
        // 'vendor/libs/AngularJS-FlowChart/flowchart/flowchart_directive.js',

        'vendor/libs/csv.js'

      ],
      app: [
        "app/js/appModules.js",
        "app/js/appConfig.js",
        //"app/js/*.js",
        "app/js/controllers/*.js",
        "app/js/controllers/**/*.js",
        "app/js/directives/*.js",
        "app/js/services/*.js",
        "app/js/filters/*.js"
      ]
    },

    css: {

      vendor: [
        //  "vendor/css/**/*.css",
        //"vendor/css/*.css",
        'vendor/bower_components/ionic/css/ionic.css',

        'vendor/bower_components/angular-material/angular-material.css',
        'vendor/bower_components/font-awesome/css/font-awesome.css',

        // "bower_components/bootstrap/dist/css/bootstrap.css"
        // 'vendor/bower_components/bootstrap/dist/css/bootstrap.css',
        'vendor/bower_components/jquery-ui/themes/base/jquery-ui.css',
        'vendor/bower_components/angular-ui-grid/ui-grid.css',

        'vendor/bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar.css',
        'vendor/bower_components/animate.css/animate.min.css',
        'vendor/bower_components/bootstrap-switch/dist/css/bootstrap2/bootstrap-switch.css',


        'vendor/bower_components/c3/c3.css',

        // ngflowchart
        'vendor/bower_components/ngFlowchart/dist/flowchart.css',
        'vendor/bower_components/ngFlowchart/dist/onedatastyle.css',

        'vendor/bower_components/angularjs-slider/dist/rzslider.css'
      ],
      app: [
        "app/css/*.css"
      ]
    }
  };
};
