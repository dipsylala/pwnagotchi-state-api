var pwnagotchi = pwnagotchi || {};

pwnagotchi.populateDisplay = function(result){
    $("#channel").innerText = result.channel_text;
    $("#aps").innerText = result.aps_text;
    $("#uptime").innerText = result.uptime;

    $("#name").innerText = result.name + ">";
    $("#face").innerText = result.face;
    $("#status").innerText = result.status;

    $("#friend_face_text").innerText = result.friend_face_text !== null ? result.friend_face_text : "";
    $("#friend_name_text").innerText = result.friend_name_text !== null ? result.friend_name_text : "";

    $("#shakes").innerText = result.pwnd_run + "(" + result.pwnd_tot + ")";
    $("#mode").innerText = result.mode;

    $("#cpu").innerText = (result.cpu * 100).toFixed(2) + "%";
    $("#temperature").innerText = result.temperature.toFixed(2) +"c";
    $("#memory").innerText = (result.memory * 100).toFixed(2) + "%"
};