let texts = [
    "Gathering inspiration...",
    "Penning your love story...",
    "Polishing with love and care...",
    "Crafting a unique masterpiece...",
    "Bringing your words to life...",
    "Finalizing the declaration of love...",
    "Surprising your loved one with the gift of words..."
]

var o = document.querySelector('#preloader').querySelector('p')

setInterval(function(){
    o.textContent = texts[Math.floor(Math.random() * texts.length)];
}, 3000);