const others = document.querySelectorAll('.other-answer')

others.forEach(checkbox => {
    const input = checkbox.parentElement.querySelector('.answer-input')
    checkbox.querySelector('input').addEventListener('click', () => {
        if (input.disabled) {
            input.disabled = false
        } else {
            input.disabled = true
            input.value = ""
        }
    })
})