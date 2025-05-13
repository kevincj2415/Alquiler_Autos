document.addEventListener('DOMContentLoaded', () => {
  // Menú responsive
  const toggleBtn = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  toggleBtn.addEventListener('click', () => {
    navLinks.classList.toggle('active'); // Cambiado a 'active' para coincidir con CSS
    toggleBtn.classList.toggle('active'); // Opcional: estilo para botón activo
  });

  // Modal
  const abrirBtn = document.getElementById('btn-abrir-formulario');
  const modal = document.getElementById('modal-formulario');
  const cerrarBtn = document.querySelector('.cerrar-modal');

  abrirBtn.addEventListener('click', () => {
    modal.style.display = 'block';
    document.body.style.overflow = 'auto'; // Bloquear scroll
  });

  const cerrarModal = () => {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restaurar scroll
  };

  cerrarBtn.addEventListener('click', cerrarModal);
  window.addEventListener('click', (e) => e.target === modal && cerrarModal());

  // ScrollReveal config
  const sr = ScrollReveal({
    reset: false,
    distance: '50px',
    duration: 800,
    delay: 100,
    easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
  });

  // Animaciones
  sr.reveal('.contenido h1', { origin: 'top' })
    .reveal('.contenido p', { origin: 'bottom', delay: 200 })
    .reveal('.car-card', {
      origin: 'bottom',
      interval: 150,
      afterReveal: (domEl) => domEl.style.opacity = 1 // Mejor transición
    });
});