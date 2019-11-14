var pwnagotchi = pwnagotchi || {};

pwnagotchi.populateDisplay = function(result){
    $("#name").innerText = result.name + ">";
    $("#face").innerText = result.face;
    $("#status").innerText = result.status;

    $("#shakes").innerText = result.pwnd_run + "(" + result.pwnd_tot + ")";
    $("#mode").innerText = result.mode;
};