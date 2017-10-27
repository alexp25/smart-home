angular.module('app').controller('navigationCtrl', ['AuthService', 'SharedProperties', '$scope',
  '$log', '$timeout', '$filter', '$state', '$location',
  '$rootScope', '$templateCache',
  '$mdSidenav', '$mdUtil', '$mdMedia', '$q', 'GlobalFcnService', 'StorageService',
  function(AuthService, SharedProperties, $scope, $log, $timeout, $filter, $state,
    $location,
    $rootScope, $templateCache, $mdSidenav, $mdUtil, $mdMedia, $q, GlobalFcnService, StorageService) {

    var NAV_SIDEBAR = 2;
    var NAV_TABS = 1;


    $scope.navstyle = NAV_TABS;
    $scope.tabSelection = {};
    $scope.fullContentHeight = 0;
    $scope.showSidenav = true;

    $scope.lockLeft = true;
    $scope.sidenavVisible = false;

    $rootScope.flagRefresh = true;

    $scope.authenticated = false;




    /*	$scope.tabSelection = {
    			lvl1: 0,
    			lvl2: 0
    	};*/
    var elementLvl1, elementLvl2;


    var isMobile = {
      Android: function() {
        return navigator.userAgent.match(/Android/i);
      },
      BlackBerry: function() {
        return navigator.userAgent.match(/BlackBerry/i);
      },
      iOS: function() {
        return navigator.userAgent.match(/iPhone|iPad|iPod/i);
      },
      Opera: function() {
        return navigator.userAgent.match(/Opera Mini/i);
      },
      Windows: function() {
        return navigator.userAgent.match(/IEMobile/i);
      },
      any: function() {
        return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
      }
    };

    $scope.menuList = [{
      name: 'Home',
      url: '#/home',
      icon: ''
      // icon: 'fa fa-home'
    }, {
      name: 'Irrigation',
      subSections: [{
        name: 'Monitor',
        url: '#/ws/monitor',
        icon: 'fa fa-tachometer'
      }, {
        name: 'Control',
        url: '#/ws/control',
        icon: 'fa fa-tachometer'
      }, {
        name: 'Setup',
        url: '#/ws/setup',
        icon: 'fa fa-wrench'
      },{
        name: 'Setup advanced',
        url: '#/ws/setup-advanced',
        icon: 'fa fa-wrench'
      }, {
        name: 'ACS',
        url: '#/ws/acs',
        icon: 'fa fa-bar-chart'
      }, {
        name: 'Program',
        url: '#/ws/program',
        icon: 'fa fa-upload'
      }]
    }, {
      name: 'Monitor',
      subSections: [
        //   {
        //   name: 'ViewAll',
        //   url: '#/monitor/view-all',
        //   icon: ''
        // },
        {
          name: 'View',
          url: '#/monitor/view',
          icon: 'fa fa-tachometer'
        }, {
          name: 'Chart',
          url: '#/monitor/chart',
          icon: 'fa fa-area-chart'
        }, {
          name: 'Schematic',
          url: '#/monitor/schematic',
          icon: 'fa fa-chain'
        }, {
          name: 'Sound',
          url: '#/monitor/sound',
          icon: 'fa fa-play'
        }
      ]
    }, {
      name: 'Settings',
      subSections: [{
          name: 'App',
          url: '#/settings/app',
          icon: 'fa fa-wrench'
        }, {
          name: 'Monitor',
          url: '#/settings/monitor',
          icon: 'fa fa-wrench'
        }, {
          name: 'Nodes',
          url: '#/settings/nodes',
          icon: 'fa fa-wrench'
        },
        // {
        //   name: 'Weather',
        //   url: '#/settings/weather',
        //   icon: ''
        // },
        {
          name: 'User',
          url: '#/settings/user',
          icon: 'fa fa-wrench'
        },
        {
          name: 'Admin',
          url: '#/settings/admin',
          icon: 'fa fa-wrench'
        }
      ]
    }, {
      name: 'Webcam',
      subSections: [{
        name: 'Server',
        url: '#/webcam/home',
        icon: 'fa fa-camera'
      },{
        name: 'Other',
        url: '#/webcam/other',
        icon: 'fa fa-camera'
      }]
    }, {
      name: 'Server',
      subSections: [{
        name: 'Main',
        url: '#/server/main',
        icon: 'fa fa-bar-chart'
      }]
    }];

    $scope.login = function() {
      $state.go('login');
    };

    function buildToggler(componentId) {
      return function() {
        $mdSidenav(componentId).toggle();
      };
    }
    // $scope.toggleLeft = buildToggler('left');

    $scope.toggleLeft = function() {
      $mdSidenav('left').toggle().then(function() {
        $scope.sidenavVisible = $mdSidenav('left').isOpen();
        console.log('sidenav toggle: ', $mdSidenav('left').isOpen());
      });
    };

    $scope.closeSidenav = function() {
      $mdSidenav('left').close()
        .then(function() {
          $log.debug("close LEFT is done");
        });
    };

    $scope.toggleSidenav = function() {
      if ($mdMedia('gt-md')) {
        $scope.lockLeft = !$scope.lockLeft;
        $scope.sidenavVisible = $scope.lockLeft;

        $rootScope.flagRefresh = false;
        $timeout(function() {
          $rootScope.flagRefresh = true;
        }, 500);

      } else {
        $scope.toggleLeft();
      }
      // console.log();
    };

    $scope.changeUrlTo = function(section) {
      if (section.hasOwnProperty('url')) {
        $location.path(section.url.replace('#', ''));
        $scope.openPage = section;

        if (!$mdMedia('gt-md')) {
          $scope.toggleLeft();
        }
        // $scope.toggleLeft();
      } else {
        section.isOpen = true;
        for (var i = 0; i < $scope.menuList.length; i++) {
          if ($scope.menuList[i] !== section) {
            $scope.menuList[i].isOpen = false;
          }
        }
      }
    };

    var selectMenuLvl1 = function(section) {
      section.isOpen = true;
      for (var i = 0; i < $scope.menuList.length; i++) {
        if ($scope.menuList[i] !== section) {
          $scope.menuList[i].isOpen = false;
        }
      }
    };

    var changeUrl = function(changedLvl) {
      if (changedLvl === 1) {
        //console.log('change lvl1');
        elementLvl1 = $scope.menuList[$scope.tabSelection.lvl1];
        if (elementLvl1) {
          if (elementLvl1.hasOwnProperty('url')) {
            $location.path(elementLvl1.url.replace('#', ''));
          }
        }
        //$scope.tabSelection.lvl2 = 0;
      } else if (changedLvl === 2) {
        //console.log('change lvl2');

        if (elementLvl1) {
          if (elementLvl1.hasOwnProperty('subSections')) {
            elementLvl2 = elementLvl1.subSections[$scope.tabSelection.lvl2];
            if (elementLvl2) {
              if (elementLvl2.hasOwnProperty('url')) {
                $location.path(elementLvl2.url.replace('#', ''));
              }
            }
          }
        }
      }
    };

    var selectMenuFromUrl = function(value) {
      var found = false;
      value = '#' + value;
      //console.log(value);
      for (var i = 0; i < $scope.menuList.length; i++) {
        var section = $scope.menuList[i];
        if (section.hasOwnProperty('url')) {
          selectMenuLvl1(section);
        }

        if (section.hasOwnProperty('subSections')) {
          for (var j = 0; j < section.subSections.length; j++) {
            var subSection = section.subSections[j];
            if (subSection.hasOwnProperty('url')) {
              if (subSection.url === value) {
                selectMenuLvl1(section);
              }
            }
          }
        }
      }
    };

    var selectTabsFromUrl = function(value) {
      //search through menu structure to find matching url and corresponding indexes for 2 way bindning with the tabs
      var found = false;
      value = '#' + value;
      //console.log(value);
      for (var i = 0; i < $scope.menuList.length; i++) {
        var menuSelection = $scope.menuList[i];
        if (menuSelection.hasOwnProperty('url')) {
          if (menuSelection.url === value) {
            $scope.tabSelection = {
              lvl1: i,
              lvl2: 0
            };
            break;
          }
        }
        if (menuSelection.hasOwnProperty('subSections')) {
          for (var j = 0; j < menuSelection.subSections.length; j++) {
            var subSection = menuSelection.subSections[j];
            if (subSection.hasOwnProperty('url')) {
              if (subSection.url === value) {
                $scope.tabSelection = {
                  lvl1: i,
                  lvl2: j
                };
                found = true;
                break;
              }
            }

          }
          if (found) {
            break;
          }
        }
      }
    };
    $rootScope.$on('$stateChangeStart',
      function(event, toState, toParams, fromState, fromParams) {

        console.log('navigationCtrl stateChangeStart to:');
        console.log(toState.name);

        if ($scope.navstyle === NAV_TABS) {
          if (toState.name === 'home') {
            $scope.tabSelection = {
              lvl1: 0,
              lvl2: 0
            };
          }
        }

        if (toState.restricted !== true) {
          if ($scope.navstyle === NAV_TABS) {
            selectTabsFromUrl($location.path());
          } else {
            selectMenuFromUrl($location.path());
          }
          //console.log('authentification check navigationCtrl');
          $scope.authenticated = AuthService.isLoggedInCheck();
          //console.log($scope.authenticated);
        }
      });

    $rootScope.$on('$viewContentLoaded',
      function(event, toState, toParams, fromState, fromParams) {
        //window.scrollTo(0, 0);
        console.log("viewContentLoaded");
      });


    /**
    this is used to be able to load user settings at app start
    i.e. navigation style
    */
    $scope.$watch(function() {
      return AuthService.isLoggedInCheck();
    }, function(newVal, oldVal, scope) {
      console.log('watch user: ', newVal);
      if (newVal === true && oldVal !== true) {
        $scope.init();
      }
    }, true);

    // var set_occupy_heigh = function() {
    //   var occupy_height = $(window).height() - $('#div_to_occupy_the_rest').offset().top;
    //   console.log("occupy_height:", occupy_height);
    //   $('#div_to_occupy_the_rest').height(
    //     occupy_height
    //   );
    // };
    // $(window).resize(function() {
    //   set_occupy_heigh();
    // });


    // $scope.saveLocalData = function() {
    //   $localStorage.message = "Hello World";
    // };
    //
    // $scope.loadLocalData = function() {
    //   $scope.localData = $localStorage.message;
    // };


    $scope.init = function() {
      console.log("navigation init");


      $scope.localStorage = StorageService.getData();
      console.log("localStorage: ", $scope.localStorage);

      if ($scope.localStorage === undefined) {
        $location.path("/config");
      } else {
        if ($scope.localStorage.url === undefined) {
          $scope.localStorage.url = '';
        }
        if ($scope.localStorage.wsurl === undefined) {
          $scope.localStorage.wsurl = 'ws://' + document.location.host;
        }
        SharedProperties.setOneProperty('url', $scope.localStorage.url);
        SharedProperties.setOneProperty('wsurl', $scope.localStorage.wsurl);
      }


      $scope.authenticated = AuthService.isLoggedInCheck();
      console.log('authenticated: ', $scope.authenticated);
      if ($scope.authenticated) {
        console.log("navigationCtrl get settings");
        GlobalFcnService.getSettings().then(function(response) {

          console.log(response);
          $scope.settings = response.data.userSettings.app;
          if ($scope.settings.navMode === true) {
            $scope.navstyle = NAV_SIDEBAR;

            if (!$mdMedia('gt-md')) {
              $scope.lockLeft = false;
              $scope.sidenavVisible = false;
            }

            /*
              if gt-md and lock left -> show sidenav, hide icon
              if gt-md and !lock left -> hide sidenav, show icon
              if !gt-md and lock left -> show sidenav
            */

          } else {
            $scope.navstyle = NAV_TABS;
          }
          if ($scope.navstyle === NAV_TABS) {
            selectTabsFromUrl($location.path());
            $scope.$watch('tabSelection.lvl1', function() {
              changeUrl(1);
              changeUrl(2);
            });
            $scope.$watch('tabSelection.lvl2', function() {
              changeUrl(2);
            });
          }


          // set_occupy_heigh();

          // $timeout(function() {
          //   $scope.authenticated = AuthService.isLoggedInCheck();
          //   console.log('authenticated: ', $scope.authenticated);
          // });
        });
      }
    };


    $scope.isSelected = function(url) {
      if ($location.path() === url.replace('#', '')) {
        return true;
      }
      return false;
    };


    /*  $(window).resize(function() {
        $scope.$apply(function() {
          console.log('resized');
          $scope.fullContentHeight = getFullHeight();
          SharedProperties.getProperty().documentSettings.fullContentHeight = $scope.fullContentHeight;
          console.log(SharedProperties.getProperty().documentSettings.fullContentHeight);
        });
      });*/

    // $scope.clearCache = function() {
    //   $templateCache.removeAll();
    //   console.log('clear cache');
    // };

  }
]);
