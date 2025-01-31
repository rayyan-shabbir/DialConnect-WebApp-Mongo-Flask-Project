// Card enlargement and active state management
document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.card-enlarge');

    cards.forEach(card => {
        card.addEventListener('click', function () {
            // Remove 'active-card' class from all cards
            cards.forEach(c => c.classList.remove('active-card'));

            // Add 'active-card' class to the clicked card
            card.classList.add('active-card');
        });
    });

    document.addEventListener('click', function (e) {
        const activeCard = document.querySelector('.card-enlarge.active-card');
        if (activeCard && !activeCard.contains(e.target)) {
            activeCard.classList.remove('active-card');
        }
    });
});

// Typewriter effect for text
document.addEventListener("DOMContentLoaded", function () {
    const textElement = document.getElementById("typewriter");
    const text = textElement.textContent;
    let i = 0;

    function typeWriter() {
        if (i < text.length) {
            textElement.innerHTML += text.charAt(i);
            i++;
            setTimeout(typeWriter, 100); // Adjust speed here
        } else {
            setTimeout(() => {
                textElement.textContent = ''; // Clear the text
                i = 0;
                typeWriter(); // Start again
            }, 1000); // Delay before starting again
        }
    }

    textElement.textContent = ''; // Clear the initial text
    typeWriter();
});

// Navbar link highlighting based on scroll position
document.addEventListener('DOMContentLoaded', function () {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');

    function changeNavLink() {
        let index = sections.length;

        while (--index && window.scrollY + 50 < sections[index].offsetTop) { }

        navLinks.forEach((link) => link.classList.remove('active'));
        navLinks[index].classList.add('active');
    }

    changeNavLink();
    window.addEventListener('scroll', changeNavLink);
});