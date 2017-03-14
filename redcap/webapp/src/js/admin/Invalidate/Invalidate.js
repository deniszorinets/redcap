/**
 * @example
 * let invalidate = new Invalidate(<server_id>);
 */
class Invalidate {
    /**
     * Constructor
     * @param serverID {number} server id to deploy
     * @param elementID {object} document element to add listener
     *
     */
    constructor(serverID, elementID) {
        this.serverID = serverID;
        this.elementID = elementID;
        this.element = document.getElementById(this.elementID);

        this.addListener();
    }

    /**
     * Add onclick listener to element
     */
    addListener() {
        const self = this;
        this.element.addEventListener('click', function () {
            self.makeDeploy();
        })
    }

    makeDeploy() {
        Ajax.ajaxRequest('/manager/invalidate/', 'POST', {serverID: this.serverID}, (data) => {});
    }
}