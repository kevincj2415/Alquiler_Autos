function abrirModalEditar() {
    document.getElementById("modal-editar").style.display = "block";
}

function cerrarModalEditar() {
    document.getElementById("modal-editar").style.display = "none";
}

// Cerrar al hacer clic fuera del modal
window.onclick = function(event) {
    const modal = document.getElementById("modal-editar");
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

function abrirModalEliminar() {
    document.getElementById("modal-eliminar").style.display = "block";
}

function cerrarModalEliminar() {
    document.getElementById("modal-eliminar").style.display = "none";
}

window.onclick = function(event) {
    const modalEliminar = document.getElementById("modal-eliminar");
    if (event.target === modalEliminar) {
        modalEliminar.style.display = "none";
    }
}