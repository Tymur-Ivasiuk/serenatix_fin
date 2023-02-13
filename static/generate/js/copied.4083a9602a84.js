var referralBtn = document.querySelector('#referral')

referralBtn.addEventListener('click', (e) => {
    navigator.clipboard.writeText(e.target.value)
    e.target.textContent = 'Copied'
})