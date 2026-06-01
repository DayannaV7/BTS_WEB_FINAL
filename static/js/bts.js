// BTS WORLD — JavaScript global

// Auto-cerrar alertas flash después de 4 segundos
document.addEventListener('DOMContentLoaded', () => {
    const alertas = document.querySelectorAll('.bts-alert');
    alertas.forEach(a => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });
});
