(function($) {
    var = StreamUpdate = Backbone.Model.extend({

        defaults : {
            "count" : 0,
            "slug"  : undefined
        }, 

        initialize : function () {
            this.openSocket();   
        },

        openSocket : function () {
            this.socket = new io.connect('/update', {resource: 'stream', port: 8082});
            this.socket.on('connect', this.onConnect);
            this.socket.on('disconnect', this.onClose);
            this.socket.on('message', this.onMessage);
        },

        onOpen : function () {

        },

        onClose : function () {

        },

        onMessage : function () {

        }
    });

    var StreamCreation = Backbone.Model.extend({

        defaults : {}

        initialize : function () {
            this.openSocket();
        },

        openSocket : function () {
            this.socket = new io.connect('/create', {resource: 'stream', port: 8082});
            this.socket.on('connect', this.onConnect);
            this.socket.on('disconnect', this.onClose);
            this.socket.on('message', this.onMessage);
        },
}
