document.addEventListener("DOMContentLoaded", () => {
    console.log("JS carregado com sucesso");

    // Exemplo: mensagem quando clicar em "Entrar"
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", (event) => {
            alert("Tentando logar...");
        });
    }
});
