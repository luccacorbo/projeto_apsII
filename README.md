# 🎯 FofoTechs – Organizador de Tarefas Gamificado

---

## 🧩 Visão Geral do Projeto
O **FofoTechs** é uma **aplicação web funcional** que combina **gestão de projetos com gamificação**, voltada para **jovens profissionais e equipes ágeis**.  

O objetivo é auxiliar empresas e colaboradores a melhorarem **produtividade, engajamento e disciplina**, transformando o cumprimento de tarefas em uma experiência **interativa e recompensadora baseada em um sistema de tabuleiro**.

---

## 🏗️ Status do Projeto
✅ **Funcional – MVP Implantado!**

O **Produto Mínimo Viável (MVP)** está completo, funcional e hospedado na nuvem.  
A aplicação inclui o **sistema de gamificação completo** (tabuleiro, saldo e recompensas) e está acessível publicamente.

➡️ **Acesse o FofoTechs aqui:**  

[https://fofotechs.app](https://fofotechs.up.railway.app/login)  

---

## 🚀 Objetivo Geral
Criar uma **plataforma de organização de tarefas** que motive usuários por meio de **mecânicas de jogo** — como um tabuleiro de progresso, acúmulo de *saldo* (moedas) e recompensas — incentivando o cumprimento de metas e o desenvolvimento de hábitos produtivos.

---

## 🎯 Objetivos Específicos
- **Organização:** permitir a criação de projetos, registro de tarefas (estilo Kanban) e gestão de membros.  
- **Gamificação:** recompensar a conclusão de tarefas com *saldo*, que permite ao usuário avançar em um tabuleiro de progresso para conquistar recompensas.  
- **Produtividade:** estimular o foco e reduzir a procrastinação no ambiente de trabalho.  
- **Engajamento:** aumentar a motivação e o senso de progresso dos colaboradores.  
- **Gestão:** fornecer uma estrutura clara para administradores de projeto gerenciarem o fluxo de trabalho.  

---

## ⚙️ Funcionalidades Implementadas
| **Categoria** | **Descrição** | **Status** |
|----------------|----------------|-------------|
| Autenticação de Usuários | Cadastro, Login e Recuperação de Senha por e-mail. | ✅ Implementado |
| Gestão de Projetos | Criação de projetos, dashboards e adição de membros. | ✅ Implementado |
| Sistema de Convites | Administradores podem convidar novos membros. | ✅ Implementado |
| Gestão de Tarefas | Kanban (Todo, Doing, Done), atribuição e prioridades. | ✅ Implementado |
| Sistema de Gamificação | Lógica de Tabuleiro, Saldo e Recompensas por posição. | ✅ Implementado |
| Histórico e Progresso | Logs de saldo gerado, recompensas e placar de líderes. | ✅ Implementado |

---

## 🧩 Stack Tecnológica Utilizada
| **Camada** | **Tecnologia / Ferramenta** |
|-------------|-----------------------------|
| Front-end | HTML5, CSS3, JavaScript |
| Back-end | Python (Framework Flask) |
| Banco de Dados | MySQL |
| Hospedagem (Infra) | Railway (App Service + Banco de Dados) |
| Ferramentas de Apoio | Git, VS Code, MySQL Workbench |

---

## 🧮 Modelagem de Dados
O modelo de dados foi **implementado com sucesso** no ambiente de produção.  
A estrutura foi projetada para suportar a lógica de gamificação de forma robusta.

**Destaques do Modelo:**
- **Tabelas de Gamificação:** `tabuleiro`, `progresso_tabuleiro`, `historico_saldo` e `historico_recompensas`;  
- **Lógica de Recompensa:** a tabela `recompensa` é baseada em *posicao* no tabuleiro do projeto;  
- **Automação:** um **TRIGGER** (`after_projeto_insert`) cria automaticamente um tabuleiro para cada novo projeto;  
- **Integridade:** o modelo segue princípios de **normalização (3FN)** com chaves primárias, estrangeiras e integridade referencial.

---

## 🧠 Justificativa
O projeto nasceu da necessidade de lidar com os desafios da **Geração Z** no ambiente corporativo — como o imediatismo, a baixa tolerância à frustração e a desorganização com prazos.  

O **FofoTechs** busca equilibrar essas duas realidades, oferecendo uma ferramenta que:
- Motiva o colaborador com **recompensas e desafios**;  
- E auxilia gestores a **acompanhar o desempenho da equipe** de forma prática e divertida.

---

## 🧩 Próximos Passos
Com o **MVP implantado**, o foco se volta para **melhorias e novas funcionalidades**:
- Refinar a **UI/UX** (Interface de Usuário) para torná-la mais moderna e responsiva;  
- Integração com **Power BI** para relatórios avançados de gestão;  
- Realizar **testes de carga e otimizações de performance** nas consultas do banco;  
- **Novas Features:** implementação de **chat em tempo real** por projeto.  

---

## 🧑‍💻 Equipe do Projeto
Trabalho desenvolvido de forma colaborativa na disciplina **Análise e Projeto de Sistemas II – UNICID**, integrando funções de **análise, modelagem, desenvolvimento e implantação (deploy)**.  

---

## 🧾 Documentação do Projeto

Os principais documentos produzidos até o momento incluem:
- **TAP (Termo de Abertura do Projeto)** – definição de escopo, objetivos e stakeholders;  
- **Análise de Requisitos** – requisitos funcionais, não funcionais e casos de uso;  
- **DER e Modelo Lógico** – estrutura do banco de dados;  
- **Registro de Partes Interessadas** – stakeholders e estratégias de engajamento.  

---

## 🌟 Impacto Esperado

O **FofoTechs** busca gerar valor tanto para colaboradores quanto para empresas, promovendo:
- Maior **engajamento e produtividade**;  
- Redução de **rotatividade**;  
- Desenvolvimento de **soft skills** como responsabilidade, organização e comprometimento;  
- E melhoria na **comunicação e cultura organizacional**.

---

## 📜 Licença
Este projeto foi desenvolvido com fins exclusivamente **acadêmicos** para a disciplina **Análise e Projeto de Sistemas II – UNICID**.  

A **reprodução total ou parcial**, **uso comercial**, **modificação** ou **redistribuição** deste software **não são permitidos** sem autorização prévia dos autores.  

© 2025 – Todos os direitos reservados à equipe do projeto **FofoTechs**.
