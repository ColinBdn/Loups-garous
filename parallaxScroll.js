document.addEventListener("scroll", () => {
    const sections = document.querySelectorAll(".section");
    const scrollPosition = window.scrollY;

    sections.forEach((section, index) => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;

        if (scrollPosition >= sectionTop - sectionHeight / 2 && 
            scrollPosition < sectionTop + sectionHeight / 2) {
            section.style.transform = "scale(1.1)"; // Zoom effect
            section.style.transition = "transform 0.5s ease-in-out";
        } else {
            section.style.transform = "scale(1)";
        }
    });
});
