// set date
const date = document.getElementById('date')
date.innerHTML = new Date().getFullYear();


//rotate on scroll
var elem = document.getElementById('hallmark');
window.addEventListener('scroll', function () {
    var value = window.scrollY * 0.25;
    elem.style.transform = `translatex(-50%) translatey(-50%) rotate(${value}deg)`;
});

//revealing effect

function reveal_y() {
    var reveals = document.querySelectorAll(".reveal_y")
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 0.1 * windowHeight;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
        // else {
        //     reveals[i].classList.remove("active");
        // }
    }
}

window.addEventListener("scroll", reveal_y);

// To check the scroll position on page load
reveal_y();

function reveal_x() {
    var reveals = document.querySelectorAll(".reveal_x")
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 0.2 * windowHeight;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
        // else {
        //     reveals[i].classList.remove("active");
        // }
    }
}

window.addEventListener("scroll", reveal_x);

// To check the scroll position on page load
reveal_x();

function reveal_y_delay() {
    var reveals = document.querySelectorAll(".reveal_y_delay")
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 0 * windowHeight;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
        // else {
        //     reveals[i].classList.remove("active");
        // }
    }
}

window.addEventListener("scroll", reveal_y_delay);

// To check the scroll position on page load
reveal_y_delay();

function reveal_x_delay() {
    var reveals = document.querySelectorAll(".reveal_x_delay")
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 0 * windowHeight;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
        // else {
        //     reveals[i].classList.remove("active");
        // }
    }
}

window.addEventListener("scroll", reveal_x_delay);

// To check the scroll position on page load
reveal_x_delay();



//customized loading

// var loader = document.getElementsByClassName('loader-wrapper');

// window.addEventListener('load', () => {
//     const preload = document.querySelector('.loader-wrapper');
//     setTimeout(function () {
//         preload.classList.add('preload-finish');
//     }, 50);
// });


//top-link reveal


window.addEventListener('scroll', function () {
    var top = document.querySelectorAll(".top-link");

    for (var i = 0; i < top.length; i++) {
        var value = window.scrollY;
        var windowHeight = window.innerHeight;
        if (value > 0.4 * windowHeight) {
            top[i].classList.add("active")
        } else {
            top[i].classList.remove("active");
        }
        console.log(value);
        console.log(windowHeight);
    }
});