var pwnagotchi = pwnagotchi || {};

pwnagotchi.stateRetrieval = (function(){
    let _retrieval = function(callback){
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
                let response = JSON.parse(this.responseText);

                let initialised = response.initialised !== "false";

                if (initialised === false){
                    const snore = $("#snore");
                    snore.innerText = snore.dataset.zeds.charAt(snore.dataset.index++);
                    if (snore.dataset.index>2) { snore.dataset.index = "0";}
                    return;
                }

                if (response.name !== undefined) {
                    window.document.title = response.name;
                }

                $.mobile.loading( 'hide' );
                callback(response)
            }
        };
        xhttp.open("GET", "/plugins/state-api/json", true);
        xhttp.send();
    };

    let initialise = function(callback){
        setInterval(_retrieval, 2000, callback)
    };

    return {
        initialise: initialise
    }
}());