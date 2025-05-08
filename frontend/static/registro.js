document.addEventListener('DOMContentLoaded', () => {
    const btnUsuario = document.getElementById('btn-usuario');
    const btnSocio = document.getElementById('btn-socio');
    const camposSocio = document.getElementById('campos-socio');
    const tipoUsuario = document.getElementById('tipo_usuario');
  
    btnUsuario.addEventListener('click', () => {
      btnUsuario.classList.add('active');
      btnSocio.classList.remove('active');
      camposSocio.style.display = 'none';
      tipoUsuario.value = 'usuario';
    });
  
    btnSocio.addEventListener('click', () => {
      btnSocio.classList.add('active');
      btnUsuario.classList.remove('active');
      camposSocio.style.display = 'block';
      tipoUsuario.value = 'socio';
    });
  });
  