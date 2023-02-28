var content_type = document.querySelector('#content_type_list').querySelectorAll('li')
var content_styles = document.querySelector('#content_styles_list').querySelectorAll('li')

var style_btn = document.querySelector('#style_button')
var content_type_input = document.querySelector('input[name="content_type"]')

var styles_input = document.querySelector('input[name="style"]')
var styles_header_content = document.querySelector('.selectStyle')

content_type.forEach((e) => {
    e.addEventListener('click', () => {
        styles_input.value = ""
        styles_header_content.innerText = "Combo Box"
        styles_header_content.style = ""
        content_styles.forEach((j) => {
            if(j.attributes.name.value == e.outerText){
                j.style.display="block"
            } else {
                j.style.display="none"
            }
        })
    })
})


style_btn.addEventListener('click', () => {
    if(content_type_input.value == "None"){
        alert("Please select content type")
    }
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
