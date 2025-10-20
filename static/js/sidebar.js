// static/js/sidebar.js

// Função para carregar projetos via API
function carregarProjetos() {
    fetch('/api/meus-projetos')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar projetos');
            }
            return response.json();
        })
        .then(projetos => {
            const container = document.getElementById('lista-projetos');
            if (!container) return;
            
            container.innerHTML = '';
            
            if (projetos.length === 0) {
                container.innerHTML = '<li class="no-projects">Nenhum projeto</li>';
                return;
            }
            
            projetos.forEach(projeto => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = `/projeto/${projeto.id_projeto}`;
                a.textContent = projeto.nome;
                a.title = projeto.descricao || 'Sem descrição';
                li.appendChild(a);
                container.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar projetos:', error);
            const container = document.getElementById('lista-projetos');
            if (container) {
                container.innerHTML = '<li class="error">Erro ao carregar</li>';
            }
        });
}

// Função para toggle do submenu
function toggleSubmenu(event) {
  event.preventDefault();
  
  var submenu = document.getElementById('workspaceSubmenu');
  if (!submenu) return;
  
  // Alterna entre none e block
  if (submenu.style.display === 'block') {
    submenu.style.display = 'none';
  } else {
    submenu.style.display = 'block';
  }
}

// Fechar ao clicar fora
document.addEventListener('click', function(event) {
  var submenu = document.getElementById('workspaceSubmenu');
  var menuLink = document.querySelector('[onclick*="toggleSubmenu"]');
  
  if (submenu && !menuLink.contains(event.target) && !submenu.contains(event.target)) {
    submenu.style.display = 'none';
  }
});


// Carregar projetos quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    carregarProjetos();
});