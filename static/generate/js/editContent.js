var editBtn = document.querySelector('#editBtn')

editBtn.addEventListener('click', function() {
    document.querySelector('#contentTitle').disabled = false
    document.querySelector('#contentText').disabled = false

    editBtn.setAttribute('style', 'display: none;')
    document.querySelector('#saveBtn').setAttribute('style', '')
})


var textarea = document.querySelector("#contentText");
textarea.addEventListener('input', autoResize, false);

function autoResize() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
}

function autoResizeStart(fieldId) {
    document.getElementById(fieldId).style.height = 'auto';
    document.getElementById(fieldId).style.height = document.getElementById(fieldId).scrollHeight + 'px';
}

autoResizeStart("contentText")