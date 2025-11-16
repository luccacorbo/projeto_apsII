// static/js/sidebar.js

// --- Função do tabuleiro.js (Mantida) ---
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

// --- Função 'toggleSubmenu' (CORRIGIDA para animação) ---
function toggleSubmenu(event) {
  event.preventDefault();
  
  const link = event.currentTarget; // O <a> que foi clicado
  const submenu = document.getElementById('workspaceSubmenu');
  if (!submenu || !link) return;

  // 1. Adiciona/Remove a classe 'active' no link para o CSS girar a seta
  link.classList.toggle('active');

  // 2. Alterna a altura do submenu (para animar)
  if (submenu.style.maxHeight) {
    // Se está aberto, fecha
    submenu.style.maxHeight = null;
  } else {
    // Se está fechado, abre
    submenu.style.maxHeight = submenu.scrollHeight + "px";
  }
}

// --- LÓGICA DO MENU HAMBURGER E OVERLAY (Mobile) ---
function setupMobileMenu() {
    const hamburger = document.querySelector('.hamburger-btn');
    const sidebar = document.querySelector('.sidebar');
    
    if (!hamburger || !sidebar) return;

    hamburger.addEventListener('click', (e) => {
        e.stopPropagation(); 
        sidebar.classList.toggle('active');
        document.body.classList.toggle('menu-active');
    });

    document.addEventListener('click', function(event) {
        const isMenuOpen = document.body.classList.contains('menu-active');
        const isClickOutside = !sidebar.contains(event.target) && !hamburger.contains(event.target);

        if (isMenuOpen && isClickOutside) {
            sidebar.classList.remove('active');
            document.body.classList.remove('menu-active');
        }
    });
}

// --- LÓGICA DO TOGGLE DO SIDEBAR (Desktop) ---
function setupDesktopToggle() {
    const toggleBtn = document.querySelector('.sidebar-toggle-btn');
    const body = document.body;

    if (!toggleBtn) return;

    // 1. Verificar a preferência salva no localStorage
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        body.classList.add('sidebar-collapsed');
    }

    // 2. Adicionar o evento de clique
    toggleBtn.addEventListener('click', () => {
        body.classList.toggle('sidebar-collapsed');
        // 3. Salvar a preferência
        localStorage.setItem('sidebarCollapsed', body.classList.contains('sidebar-collapsed'));
    });
}


// --- Função 'Fechar ao clicar fora' (Submenu) ---
function setupSubmenuClickOutside() {
    document.addEventListener('click', function(event) {
        var submenu = document.getElementById('workspaceSubmenu');
        // MUDANÇA: Corrigido o seletor
        var menuLink = document.querySelector('.menu-link[onclick*="toggleSubmenu"]');
        
        if (!submenu || !menuLink) return;

        // Se o submenu estiver aberto E o clique for fora dele E fora do link que o abre
        if (submenu.style.maxHeight && !menuLink.contains(event.target) && !submenu.contains(event.target)) {
            submenu.style.maxHeight = null;
            menuLink.classList.remove('active'); // Gira a seta de volta
        }
    });
}

// Carregar tudo quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    carregarProjetos();
    setupMobileMenu(); 
    setupDesktopToggle();
    setupSubmenuClickOutside(); 
});