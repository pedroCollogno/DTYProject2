import config from "./config";

function listenToServer(callback) {
  const path = config.API_PATH;
  const socketRef = new WebSocket(path);

  socketRef.onopen = function() {
    console.log("WebSocket is now open");
  };

  socketRef.onmessage = function(e) {
    callback(e.data);
  };

  socketRef.onerror = function(e) {
    console.log(e.message);
  };

  socketRef.onclose = function() {
    console.log("WebSocket is now closed");
  };
}

export { listenToServer };