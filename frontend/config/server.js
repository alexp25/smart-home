/* Define custom server-side HTTP routes for lineman's development server
 *   These might be as simple as stubbing a little JSON to
 *   facilitate development of code that interacts with an HTTP service
 *   (presumably, mirroring one that will be reachable in a live environment).
 *
 * It's important to remember that any custom endpoints defined here
 *   will only be available in development, as lineman only builds
 *   static assets, it can't run server-side code.
 *
 * This file can be very useful for rapid prototyping or even organically
 *   defining a spec based on the needs of the client code that emerge.
 *
 */

module.exports = {
  drawRoutes: function(app) {

    app.use(function(req, res, next) {
      res.header("Access-Control-Allow-Origin", "*");
      res.header("Access-Control-Allow-Headers", "X-Requested-With");
      next();
    });

    app.post('/login', function(req, res) {
      res.json({
        message: 'logging in!'
      });
    });


    // app.get('/isLoggedIn', function(req, res) {
    //   res.json({
    //     result: true
    //   });
    // });

    app.post('/logout', function(req, res) {
      res.json({
        message: 'logging out!'
      });
    });

    app.get('/books', function(req, res) {
      res.json([{
          title: 'Great Expectations',
          author: 'Dickens'
        },
        {
          title: 'Foundation Series',
          author: 'Asimov'
        },
        {
          title: 'Treasure Island',
          author: 'Stephenson'
        }
      ]);
    });
  }
};
