var content_type = document.querySelector('#content_type_list').querySelectorAll('li')
var content_styles = document.querySelector('#content_styles_list').querySelectorAll('li')

content_type.forEach((e) => {
    e.addEventListener('click', () => {
        content_styles.forEach((j) => {
            if(j.attributes.name.value == e.outerText){
                j.style.display="block"
            } else {
                j.style.display="none"
            }
        })
    })
})

document.addEventListener('DOMContentLoaded', function(){
    var p = content_type[0].parentElement.parentElement.querySelector('.select_current').innerText
    if(p){
        content_styles.forEach((j) => {
            if(j.attributes.name.value == p){
                j.style.display="block"
            } else {
                j.style.display="none"
            }
        })
    }
})
