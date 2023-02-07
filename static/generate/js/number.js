const inputs = document.querySelectorAll('.number-input')

inputs.forEach(number => {
    const input = number.querySelector('input[type="number"]')
    const plusBtn = number.querySelector('.plus')
    const minusBtn = number.querySelector('.minus')

    plusBtn.addEventListener('click', () => {
        input.value -= -1
        input.style.opacity = 1
    })
    minusBtn.addEventListener('click', () => {
        if (input.value > 0) {
            input.value -= 1
            if (input.value == 0) {
                input.style.opacity = 0.5
            }
        }
    })
})