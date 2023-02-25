// set date
const date = document.getElementById('date')
date.innerHTML = new Date().getFullYear();


//rotate on scroll
var elem = document.getElementById('hallmark');
window.addEventListener('scroll', function () {
    var value = window.scrollY * 0.25;
    elem.style.transform = `translatex(-50%) translatey(-50%) rotate(${value}deg)`;
});

// close links
const navToggle = document.querySelector('.nav-toggle')
const linksContainernavToggle = document.querySelector('.links-container')
const links = document.querySelector('.links')

navToggle.addEventListener('click', function () {

})