// Smooth scroll for navigation links
document.addEventListener('DOMContentLoaded', function () {
    const header = document.getElementById('main-header');

    function getHeaderOffset() {
        if (header) {
            return header.getBoundingClientRect().height + 12;
        }
        return 12;
    }

    function scrollToTarget(target) {
        if (!target) return;
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
        const offset = getHeaderOffset();
        const top = window.scrollY + target.getBoundingClientRect().top - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
    }

    function resolveFragment(hash) {
        if (!hash || hash.length < 2) return null;
        const id = hash.substring(1);
        return document.getElementById(id);
    }

    function handleFragmentNavigation(hash, pushState) {
        const target = resolveFragment(hash);
        if (target) {
            if (pushState && window.location.hash !== hash) {
                window.history.pushState(null, '', hash);
            }
            // Use a small delay to ensure layout is settled
            setTimeout(function () {
                scrollToTarget(target);
            }, 50);
        }
    }

    // Handle initial fragment navigation
    if (window.location.hash && window.location.hash.length > 1) {
        handleFragmentNavigation(window.location.hash, false);
    }

    // Handle mobile navigation toggle
    const navToggle = document.getElementById('nav-toggle');
    const navLinksList = document.querySelector('.nav-links');

    if (navToggle && navLinksList) {
        navToggle.addEventListener('click', function () {
            const isOpen = navLinksList.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', String(isOpen));
        });
    }

    // Handle click navigation
    const navLinks = document.querySelectorAll('#main-nav a[href^="#"]');

    navLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#') && href.length > 1) {
                const target = resolveFragment(href);
                if (target) {
                    e.preventDefault();
                    // Collapse mobile menu before measuring scroll position
                    if (navToggle && navLinksList) {
                        navLinksList.classList.remove('open');
                        navToggle.setAttribute('aria-expanded', 'false');
                    }
                    // Update URL/history before scrolling
                    if (window.location.hash !== href) {
                        window.history.pushState(null, '', href);
                    }
                    scrollToTarget(target);
                }
            }
        });
    });

    // Handle history traversal (Back/Forward)
    window.addEventListener('popstate', function () {
        // Collapse mobile menu before measuring scroll position
        if (navToggle && navLinksList) {
            navLinksList.classList.remove('open');
            navToggle.setAttribute('aria-expanded', 'false');
        }
        handleFragmentNavigation(window.location.hash, false);
    });

    // Handle hashchange (e.g., manual URL bar edits)
    window.addEventListener('hashchange', function () {
        handleFragmentNavigation(window.location.hash, false);
    });
});
