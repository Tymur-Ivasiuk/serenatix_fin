var finishBtn = document.querySelector('#finish')

finishBtn.addEventListener('click', () => {
    document.querySelector('main').classList.add("disable-load")
    document.querySelector('#preloader').classList.remove("disable-load")
})