/**
 * Created by nekmo on 18/08/15.
 */
var WebSocketFactory = function($websocket, $q, $mdToast, $mdDialog, DialogMessage) {

    // Open a WebSocket connection
    var dataStream = $websocket(sprintf('ws://%s%s', document.location.host, websocket_path));

    // Diccionario con los ids de aquellas peticiones que se han hecho que están esperando una respuesta.
    var waiting_responses = {};

    dataStream.onMessage(function(message) {
        var data = JSON.parse(message.data);
        var id = data.id;
        if(waiting_responses[id]){
            var waiting = waiting_responses[id];
            if(data.status != 'error'){
                if(data.end == true){
                    // Lo eliminamos de los que esperan respuesta si está como end == true
                    _.remove(waiting_responses, function(x){ return waiting == x });
                }
                waiting.resolve(data);
            } else {
                waiting.reject(data);
            }
        } else {

        }
    });

    dataStream.onClose(function(){
        DialogMessage.critical('cerrada conexión con servidor',
            'La conexión que se mantenía entre el servidor y su navegador, se ha cerrado por alguna razón.',
            'Esto puede ser debido a un problema de conexión (bien por su parte o del servidor), o que el' +
            ' servidor haya caído (desconexión, reinicio, etc.).',
            'Recargue la ventana. Si el problema persistiese, compruebe su conexión. Si nada de lo anterior' +
            ' funcionase, contacte con el administrador del servidor.'
        );
    });

    dataStream.onError(function(){
        DialogMessage.error('Error en la conexión con el servidor',
                    'Ha habido un error en la conexión entre usted y el servidor.',
                    'El error puede ser debido a un fallo de conexión, o un error de programación.');

    });

    var create_stanza = function(method){
        var stanza = {
            'id': UUIDjs.create(1).hex
        };
        if(method){
            stanza['method'] = method;
        }
        return stanza
    };

    return {
          get: function (data) {
              if(!data){
                  data = {};
              }
              data = _.merge(create_stanza(), data);
              dataStream.send(JSON.stringify(data));
              return $q(function(resolve, reject){
                  // Añado a la cola la petición con sus resolve y reject para que se ejecuten con la respuesta
                  var waiting = {};
                  waiting.resolve = resolve;
                  waiting.reject = reject;
                  waiting_responses[data.id] = waiting;
              });
          }
      };
};

app.factory('WebSocket', WebSocketFactory);

