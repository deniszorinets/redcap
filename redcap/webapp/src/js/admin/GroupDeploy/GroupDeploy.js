/**
 * @example
 * let deploy = new GroupDeploy(<server_id>);
 */
class GroupDeploy {
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
        Ajax.ajaxRequest('/manager/deploy_group/', 'POST', {serverID: this.serverID}, (data) => {});
    }
}