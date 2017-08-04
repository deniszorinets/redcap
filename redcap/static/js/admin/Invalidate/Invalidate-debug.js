'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
 * @example
 * let invalidate = new Invalidate(<server_id>);
 */
var Invalidate = function () {
    /**
     * Constructor
     * @param serverID {number} server id to deploy
     * @param elementID {object} document element to add listener
     *
     */
    function Invalidate(serverID, elementID) {
        _classCallCheck(this, Invalidate);

        this.serverID = serverID;
        this.elementID = elementID;
        this.element = document.getElementById(this.elementID);

        this.addListener();
    }

    /**
     * Add onclick listener to element
     */


    _createClass(Invalidate, [{
        key: 'addListener',
        value: function addListener() {
            var self = this;
            this.element.addEventListener('click', function () {
                self.makeDeploy();
            });
        }
    }, {
        key: 'makeDeploy',
        value: function makeDeploy() {
            Ajax.ajaxRequest('/manager/invalidate/', 'POST', { serverID: this.serverID }, function (data) {});
        }
    }]);

    return Invalidate;
}();
//# sourceMappingURL=Invalidate.js.map
