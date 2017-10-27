angular.module('app').controller('monitorSchematicCtrl', ['$scope', '$timeout',
  '$log', '$http',
  function($scope, $timeout, $log, $http) {
    $scope.hasData = true;

    //
    // Code for the delete key.
    //
    var deleteKeyCode = 46;

    //
    // Code for control key.
    //
    var ctrlKeyCode = 17;

    //
    // Set to true when the ctrl key is down.
    //
    var ctrlDown = false;

    //
    // Code for A key.
    //
    var aKeyCode = 65;

    //
    // Code for esc key.
    //
    var escKeyCode = 27;

    //
    // Selects the next node id.
    //
    var nextNodeID = 10;

    //
    // Setup the data-model for the chart.
    //
    var chartDataModel = {

      nodes: [{
          name: "Sensor 1",
          id: 0,
          x: 25,
          y: 247,
          width: 200,
          inputConnectors: [],
          outputConnectors: [{
              name: "humidity",
            },
            {
              name: "temperature",
            },
            {
              name: "light",
            },
          ],
        },

        {
          name: "Controller 1",
          id: 1,
          x: 352,
          y: 107,
          width: 200,
          inputConnectors: [{
            name: "input 1",
          }, {
            name: "input 2",
          }],
          outputConnectors: [{
            name: "output",
          }],
        },

        {
          name: "Actuator 1",
          id: 2,
          x: 633,
          y: 355,
          width: 200,
          inputConnectors: [{
            name: "input",
          }],
          outputConnectors: [],
        },

      ],

      connections: [{
          name: 'Connection 1',
          source: {
            nodeID: 0,
            connectorIndex: 2,
          },

          dest: {
            nodeID: 1,
            connectorIndex: 0,
          },
        },
        {
          name: 'Connection 2',
          source: {
            nodeID: 1,
            connectorIndex: 0,
          },

          dest: {
            nodeID: 2,
            connectorIndex: 0,
          },
        },

      ]
    };

    //
    // Event handler for key-down on the flowchart.
    //
    $scope.keyDown = function(evt) {
      console.log("key down: ", evt.keyCode);
      if (evt.keyCode === ctrlKeyCode) {

        ctrlDown = true;
        evt.stopPropagation();
        evt.preventDefault();
      }
    };

    //
    // Event handler for key-up on the flowchart.
    //
    $scope.keyUp = function(evt) {
      console.log("key up: ", evt.keyCode);
      if (evt.keyCode === deleteKeyCode) {
        //
        // Delete key.
        //
        $scope.chartViewModel.deleteSelected();
      }

      if (evt.keyCode === aKeyCode && ctrlDown) {
        //
        // Ctrl + A
        //
        $scope.chartViewModel.selectAll();
      }

      if (evt.keyCode === escKeyCode) {
        // Escape.
        $scope.chartViewModel.deselectAll();
      }

      if (evt.keyCode === ctrlKeyCode) {
        ctrlDown = false;

        evt.stopPropagation();
        evt.preventDefault();
      }
    };

    //
    // Add a new node to the chart.
    //
    $scope.addNewNode = function() {

      var nodeName = prompt("Enter a node name:", "New node");
      if (!nodeName) {
        return;
      }

      //
      // Template for a new node.
      //
      var newNodeDataModel = {
        name: nodeName,
        id: nextNodeID++,
        x: 0,
        y: 0,
        inputConnectors: [{
            name: "X"
          },
          {
            name: "Y"
          },
          {
            name: "Z"
          }
        ],
        outputConnectors: [{
            name: "1"
          },
          {
            name: "2"
          },
          {
            name: "3"
          }
        ],
      };

      $scope.chartViewModel.addNode(newNodeDataModel);
    };

    //
    // Add an input connector to selected nodes.
    //
    $scope.addNewInputConnector = function() {
      var connectorName = prompt("Enter a connector name:", "New connector");
      if (!connectorName) {
        return;
      }

      var selectedNodes = $scope.chartViewModel.getSelectedNodes();
      for (var i = 0; i < selectedNodes.length; ++i) {
        var node = selectedNodes[i];
        node.addInputConnector({
          name: connectorName,
        });
      }
    };

    //
    // Add an output connector to selected nodes.
    //
    $scope.addNewOutputConnector = function() {
      var connectorName = prompt("Enter a connector name:", "New connector");
      if (!connectorName) {
        return;
      }

      var selectedNodes = $scope.chartViewModel.getSelectedNodes();
      for (var i = 0; i < selectedNodes.length; ++i) {
        var node = selectedNodes[i];
        node.addOutputConnector({
          name: connectorName,
        });
      }
    };

    //
    // Delete selected nodes and connections.
    //
    $scope.deleteSelected = function() {

      $scope.chartViewModel.deleteSelected();
    };

    //
    // Create the view-model for the chart and attach to the scope.
    //
    $scope.chartViewModel = new flowchart.ChartViewModel(chartDataModel);
    $scope.init = function() {

      console.log($scope.chartViewModel);

    };

    $scope.$on('$destroy', function(event) {});
  }
]);
