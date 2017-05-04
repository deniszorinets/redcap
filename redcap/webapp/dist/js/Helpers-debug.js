"use strict";

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Cookie = function () {
    function Cookie() {
        _classCallCheck(this, Cookie);
    }

    _createClass(Cookie, null, [{
        key: "getCookie",
        value: function getCookie(name) {
            var matches = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"));
            return matches ? decodeURIComponent(matches[1]) : undefined;
        }
    }]);

    return Cookie;
}();

var Ajax = function () {
    function Ajax() {
        _classCallCheck(this, Ajax);
    }

    _createClass(Ajax, null, [{
        key: "ajaxRequest",
        value: function ajaxRequest(action, method, data, callback) {
            var xhr = new XMLHttpRequest();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        callback(JSON.parse(xhr.responseText));
                    } else {
                        error(xhr.responseText);
                    }
                }
            };

            xhr.open(method, action, true);
            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
            xhr.setRequestHeader("X-CSRFToken", Cookie.getCookie('csrftoken'));
            xhr.send(JSON.stringify(data));
        }
    }]);

    return Ajax;
}();
//# sourceMappingURL=Helpers.js.map
