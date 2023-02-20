var copyBtn = document.querySelector('.copy-btn')
var title = document.querySelector('#contentTitle')
var text = document.querySelector('#contentText')

copyBtn.addEventListener('click', ()=>{
    navigator.clipboard.writeText(title.value + "\n\n" + text.textContent)
    copyBtn.setAttribute('data-tooltip', 'Copied!')
})