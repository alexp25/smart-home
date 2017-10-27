angular.module("app").factory('VideoFactory', function($websocket) {
      // Open a WebSocket connection
      var dataStream = $websocket('wss://localhost:8000/stream/webrtc');

      var collection = [];

      dataStream.onMessage(function(message) {
        collection.push(JSON.parse(message.data));
      });

      var methods = {
        collection: collection,
        get: function() {
          dataStream.send(JSON.stringify({ action: 'get' }));
        }
      };

      return methods;
    });
