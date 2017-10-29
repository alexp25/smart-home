angular.module('app').config(['$interpolateProvider', '$stateProvider', '$urlRouterProvider',
  '$mdThemingProvider', '$httpProvider', '$locationProvider',
  function($interpolateProvider, $stateProvider, $urlRouterProvider, $mdThemingProvider, $httpProvider, $locationProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');

    $httpProvider.defaults.withCredentials = true;

    // $locationProvider.html5Mode(true);
 

    $mdThemingProvider.theme('default')
      .primaryPalette('blue-grey', {
        'default': '600', // by default use shade 400 from the pink palette for primary intentions
        'hue-1': '100', // use shade 100 for the <code>md-hue-1</code> class
        'hue-2': '600', // use shade 600 for the <code>md-hue-2</code> class
        'hue-3': 'A100' // use shade A100 for the <code>md-hue-3</code> class
      })
      .accentPalette('blue-grey', {
        'default': '400' // use shade 200 for default, and keep all other shades the same
      })

    // .backgroundPalette('grey', {
    //   'default': 'A100'
    // })

    .warnPalette('blue-grey');

    $mdThemingProvider.theme('dark-indigo').backgroundPalette('indigo', {
      'default': '300'
    }).dark();
    $mdThemingProvider.theme('dark-orange').backgroundPalette('orange').dark();
    $mdThemingProvider.theme('dark-purple').backgroundPalette('deep-purple').dark();
    $mdThemingProvider.theme('dark-blue').backgroundPalette('blue').dark();

    //  .foregroundPalette[3] = "rgba(198,198,198,0.9)"; // used by md-input-container
    /*
    red, pink, purple, deep-purple, indigo, blue, light-blue, cyan, teal, green, light-green, lime, yellow, amber, orange, deep-orange, brown, grey, blue-grey, custom-palette
    */


    //$urlRouterProvider.otherwise('/home');
    $urlRouterProvider.otherwise(function($injector, $location) {
      var $state = $injector.get("$state");
      $state.go("home");
    });


    $stateProvider
      .state('root', {
        url: '',
        abstract: true,
        access: {
          restricted: false
        },
        views: {
          /*'header': {
            templateUrl: 'static/templates/header.html'
          }*/
        }
      })
      .state('config', {
        url: '/config',
        access: {
          restricted: false
        },
        views: {
          /*'header': {
              templateUrl: 'static/templates/header.html'
            },*/
          'content': {
            templateUrl: 'templates/config.html',
            controller: 'configCtrl'
          }
        }
      })
      .state('login', {
        url: '/login',
        access: {
          restricted: false
        },
        views: {
          /*'header': {
              templateUrl: 'static/templates/header.html'
            },*/
          'content': {
            templateUrl: 'templates/login.html',
            controller: 'loginCtrl'
          }
        }
      })
      .state('register', {
        url: '/register',
        access: {
          restricted: false
        },
        views: {
          /*'header': {
              templateUrl: 'static/templates/header.html'
            },*/
          'content': {
            templateUrl: 'templates/register.html',
            controller: 'registerCtrl'
          }
        }
      })

    .state('home', {
      url: '/home',
      access: {
        restricted: true
      },
      views: {
        /*  'header': {
            templateUrl: 'static/templates/header.html'
          },
          'navigation': {
            templateUrl: 'static/templates/navigation.html',
            controller: 'navigationCtrl'
          },*/
        'content': {
          templateUrl: 'templates/home.html',
          controller: 'homeCtrl'
        }
      }
    })

    .state('webcam-home', {
      url: '/webcam/home',
      access: {
        restricted: true
      },
      views: {
        'content': {
          templateUrl: 'templates/webcam/home.html',
          controller: 'webcamHomeCtrl'
        }
      }
    })

    .state('webcam-other', {
      url: '/webcam/other',
      access: {
        restricted: true
      },
      views: {
        'content': {
          templateUrl: 'templates/webcam/other.html',
          controller: 'webcamOtherCtrl'
        }
      }
    })
    .state('ws-monitor', {
        url: '/ws/monitor',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/ws/monitor.html',
            controller: 'wsMonitorCtrl'
          }
        }
      })
    .state('ws-control', {
        url: '/ws/control',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/ws/control.html',
            controller: 'wsControlCtrl'
          }
        }
      })
      .state('ws-acs', {
        url: '/ws/acs',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/ws/acs.html',
            controller: 'wsAcsCtrl'
          }
        }
      })
      .state('ws-setup', {
        url: '/ws/setup',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/ws/setup.html',
            controller: 'wsSetupCtrl'
          }
        }
      })
      .state('ws-setup-advanced', {
        url: '/ws/setup-advanced',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/ws/setup-advanced.html',
            controller: 'wsSetupAdvancedCtrl'
          }
        }
      })
    .state('ws-program', {
        url: '/ws/program',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/ws/program.html',
            controller: 'wsProgramCtrl'
          }
        }
      })
      .state('settings-app', {
        url: '/settings/app',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/settings/app.html',
            controller: 'settingsAppCtrl'
          }
        }
      })
      .state('settings-user', {
        url: '/settings/user',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/settings/user.html',
            controller: 'settingsUserCtrl'
          }
        }
      })
      .state('settings-admin', {
        url: '/settings/admin',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/settings/admin.html',
            controller: 'settingsAdminCtrl'
          }
        }
      })
      .state('settings-nodes', {
        url: '/settings/nodes',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/settings/nodes.html',
            controller: 'settingsNodesCtrl'
          }
        }
      })
      .state('settings-weather', {
        url: '/settings/weather',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/settings/weather.html',
            controller: 'settingsWeatherCtrl'
          }
        }
      })
      // .state('monitor-view-all', {
      //   url: '/monitor/view-all',
      //   access: {
      //     restricted: true
      //   },
      //   views: {
      //     'content': {
      //       templateUrl: 'templates/monitor/view-all.html',
      //       controller: 'monitorViewAllCtrl'
      //     }
      //   }
      // })
      .state('monitor-view', {
        url: '/monitor/view',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/view.html',
            controller: 'monitorViewCtrl'
          }
        }
      })
      .state('monitor-chart', {
        url: '/monitor/chart',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/chart.html',
            controller: 'monitorChartCtrl'
          }
        }
      })
      .state('monitor-schematic', {
        url: '/monitor/schematic',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/schematic.html',
            controller: 'monitorSchematicCtrl'
          }
        }
      })
      .state('monitor-sound', {
        url: '/monitor/sound',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/sound.html',
            controller: 'monitorSoundCtrl'
          }
        }
      })
      .state('settings-monitor', {
        url: '/settings/monitor',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/settings/monitor.html',
            controller: 'settingsMonitorCtrl'
          }
        }
      })
      .state('server-main', {
        url: '/server/main',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/server/main.html',
            controller: 'serverMainCtrl'
          }
        }
      })
      .state('test', {
        url: '/test',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/test.html',
            controller: 'testCtrl'
          }
        }
      });
  }
]);


// angular.module('app').config(function(NodeTemplatePathProvider) {
//   NodeTemplatePathProvider.setTemplatePath("templates/libs/flowchart/node.html");
// });

angular.module('app').run(['$rootScope', '$state', 'AuthService', 'StorageService', function($rootScope, $state,
  AuthService, StorageService) {

  // $rootScope.localStorageData = StorageService.getData();
  // console.log("localStorage: ", $rootScope.localStorageData);

  $rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState,
    fromParams) {
    console.log('appConfig state change start');
    console.log('from: ' + fromState.name);
    console.log('to:   ' + toState.name);
    if (toState.access.restricted && !AuthService.isLoggedInCheck()) {
      event.preventDefault();
      // console.log("localStorage: ", $rootScope.localStorageData);
      // if ($rootScope.localStorageData === undefined) {
      //   console.log("local storage is undefined");
      // }
      console.log('appConfig authentification check');
      AuthService.isLoggedInCheckServer()
        .then(function(promise) {
          console.log('appConfig auth true');
          $state.go(toState, toParams);
        })
        .catch(function(error) {
          console.log('appConfig auth false');
          $state.go('login');
        });
    } else {
      console.log('isLoggedIn: ', AuthService.isLoggedInCheck());
    }
  });

  $rootScope.$on('$destroy', function() {
    alert('closed page');
  });
}]);
