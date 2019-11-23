
function dropHandler(ev) {
    ev.preventDefault();

    if (ev.dataTransfer.items) {
        if (ev.dataTransfer.items[0].kind === 'file') {
            var file = ev.dataTransfer.items[0].getAsFile();
            document.getElementById('output').innerHTML= '<strong>' + file.name + '</strong>';
            document.getElementById('uploadimage').innerHTML.src = file.name;
        }
    } else {
        document.getElementById('output').innerHTML= '<strong>' + ev.dataTransfer.files[0].name + '</strong>';
        document.getElementById('uploadimage').innerHTML.src = ev.dataTransfer.files[0].name;
    }
}

function addFile() {
    document.getElementById("file").click();
};

document.getElementById("file").addEventListener("change", function(){
    if(document.getElementById("file").value){
        document.getElementById('output').innerHTML= '<strong>' + document.getElementById("file").value + '</strong>';
    } else {
        document.getElementById('output').innerHTML='<strong>Please upload a potential picture with crack</strong>';
    }
});

function dragOverHandler(ev) {
    ev.preventDefault();
}

