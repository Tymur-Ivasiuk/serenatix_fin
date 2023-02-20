var finishBtn = document.getElementById('finish');

document.addEventListener('keypress', (event)=>{
    let keyCode = event.keyCode ? event.keyCode : event.which;
    if(keyCode === 13) {
        finishBtn.click();
    }
});