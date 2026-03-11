/* ===== Lamzai Solicitors – script.js ===== */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- Navbar scroll behaviour ---------- */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mobile nav drawer ---------- */
  const toggle = document.querySelector('.nav-toggle');
  const mobileOverlay = document.getElementById('mobileOverlay');

  if (toggle && mobileOverlay) {
    const openMenu = () => {
      mobileOverlay.classList.add('open');
      mobileOverlay.setAttribute('aria-hidden', 'false');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.classList.add('open');
      document.body.style.overflow = 'hidden';
    };

    const closeMenu = () => {
      mobileOverlay.classList.remove('open');
      mobileOverlay.setAttribute('aria-hidden', 'true');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.classList.remove('open');
      document.body.style.overflow = '';
    };

    toggle.addEventListener('click', () => {
      mobileOverlay.classList.contains('open') ? closeMenu() : openMenu();
    });

    // Close button inside panel
    const closeBtn = mobileOverlay.querySelector('.mob-close');
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);

    // Close on backdrop click
    const backdrop = mobileOverlay.querySelector('.mob-backdrop');
    if (backdrop) backdrop.addEventListener('click', closeMenu);

    // Close on nav link click
    mobileOverlay.querySelectorAll('.mob-link').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    // Close on CTA click
    const mobCta = mobileOverlay.querySelector('.mob-cta');
    if (mobCta) mobCta.addEventListener('click', closeMenu);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mobileOverlay.classList.contains('open')) closeMenu();
    });
  }

  /* ---------- Active nav link ---------- */
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mob-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  /* ---------- Smooth scroll for anchor links ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ---------- Back to top button ---------- */
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', () => {
      backToTop.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- Animate stat counters ---------- */
  const statNumbers = document.querySelectorAll('.stat-number[data-target]');
  if (statNumbers.length) {
    const animateCounter = (el) => {
      const target = el.getAttribute('data-target');
      const suffix = el.getAttribute('data-suffix') || '';
      const prefix = el.getAttribute('data-prefix') || '';
      const isFloat = target.includes('.');
      const end = parseFloat(target);
      const duration = 1800;
      const startTime = performance.now();

      const step = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = eased * end;
        el.textContent = prefix + (isFloat ? current.toFixed(1) : Math.floor(current).toLocaleString()) + suffix;
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    statNumbers.forEach(el => observer.observe(el));
  }

  /* ---------- Scroll reveal animations ---------- */
  const revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    revealEls.forEach(el => revealObserver.observe(el));
  }

  /* ---------- Contact form ---------- */
  const form = document.getElementById('contactForm');
  if (form) {
    const successMessage = document.getElementById('formSuccess');

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      // Basic validation
      const required = form.querySelectorAll('[required]');
      let valid = true;
      required.forEach(field => {
        field.style.borderColor = '';
        if (!field.value.trim()) {
          field.style.borderColor = '#e53e3e';
          valid = false;
        }
      });

      // Email format check
      const emailField = form.querySelector('#email');
      if (emailField && emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
        emailField.style.borderColor = '#e53e3e';
        valid = false;
        showToast('Please enter a valid email address.', 'error');
        return;
      }

      if (!valid) {
        showToast('Please fill in all required fields.', 'error');
        return;
      }

      // Show loading state
      const submitBtn = form.querySelector('.form-submit');
      submitBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg> Sending…';
      submitBtn.disabled = true;

      // Build template parameters
      const templateParams = {
        from_name:  form.querySelector('#name').value.trim(),
        from_email: form.querySelector('#email').value.trim(),
        phone:      form.querySelector('#phone').value.trim() || 'Not provided',
        case_type:  form.querySelector('#caseType').value,
        message:    form.querySelector('#message').value.trim()
      };

      // Send enquiry email to the firm, then send auto-reply to the client
      emailjs.send('service_8vnoxfw', 'template_c2jvcjk', templateParams)
        .then(() => {
          form.style.display = 'none';
          if (successMessage) successMessage.style.display = 'block';
          showToast('Your message has been sent! We will be in touch shortly.');
          form.reset();
          // Send auto-reply to client
          return emailjs.send('service_8vnoxfw', 'template_o5vu0tt', templateParams);
        })
        .then(() => {
          console.log('Auto-reply sent successfully.');
        })
        .catch((error) => {
          console.error('EmailJS error:', error);
        });
    });

    // Remove red border on input
    form.querySelectorAll('input, select, textarea').forEach(field => {
      field.addEventListener('input', () => { field.style.borderColor = ''; });
    });
  }

  /* ---------- Toast notification ---------- */
  function showToast(message, type = 'success') {
    let toast = document.querySelector('.toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    const icon = type === 'error'
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e53e3e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38a169" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;

    toast.innerHTML = icon + message;
    if (type === 'error') toast.style.borderLeftColor = '#e53e3e';
    else toast.style.borderLeftColor = 'var(--gold)';

    requestAnimationFrame(() => {
      toast.classList.add('show');
      clearTimeout(toast._timer);
      toast._timer = setTimeout(() => toast.classList.remove('show'), 4000);
    });
  }

  /* ---------- Spinning loader style ---------- */
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin { to { transform: rotate(360deg); } }
    .spin { animation: spin 0.8s linear infinite; }
    .reveal { opacity: 0; transform: translateY(28px); transition: opacity 0.6s ease, transform 0.6s ease; }
    .reveal.revealed { opacity: 1; transform: translateY(0); }
  `;
  document.head.appendChild(style);

});
