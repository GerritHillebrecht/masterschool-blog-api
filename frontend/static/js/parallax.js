window.addEventListener('scroll', function() {
    const heroInner = document.querySelector('.hero-inner');
    const heroText = document.querySelector(".hero-text")
    const scrolled = window.scrollY;
    const rate = scrolled * 0.35;
    const rate_text = scrolled * 0.4;

    heroInner.style.transform = `translateY(${rate}px)`;
    heroText.style.transform = `translateY(${rate_text}px)`;
});
