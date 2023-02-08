var referalBtn = document.querySelector('#referal')

referalBtn.addEventListener('click', (e) => {
    navigator.clipboard.writeText(e.target.value)
    e.target.textContent = 'Copied'
})