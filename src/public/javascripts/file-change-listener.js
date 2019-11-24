document.getElementById("fileInputSelector").addEventListener('change', function () {
    console.log("EVENT WAS FIRED");

    const fileSelect = document.getElementById("fileInputSelector");
    const fileInputName = document.getElementById("fileInputName");

    if(fileSelect.value) {
        const filePath = fileSelect.value;
        const split = filePath.split("\\");
        fileInputName.innerHTML = split[split.length - 1];
    } else {
        fileInputName.innerHTML = 'Choose image';
    }
});
