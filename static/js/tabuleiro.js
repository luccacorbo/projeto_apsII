const TOTAL_CASAS = 30;

// layout: 5 linhas x 6 colunas
const linhas = [
  [1, 2, 3, 4, 5, 6],
  [12,11,10,9,8,7],
  [13,14,15,16,17,18],
  [24,23,22,21,20,19],
  [25,26,27,28,29,30]
];

let posicao = 1;
const tabuleiro = document.getElementById("tabuleiro");
const dadoEl = document.getElementById("dado");
const resNum = document.getElementById("res-num");

function desenharTabuleiro(){
  tabuleiro.innerHTML = "";
  linhas.forEach((linha, idx) => {
    const L = document.createElement("div");
    L.className = "linha" + (idx % 2 ? " invertida" : "");
    linha.forEach((num) => {
      const div = document.createElement("div");
      div.className = "casa";
      const R = recompensas.find(r => +r.posicao === num);
      if (R){
        div.classList.add("recompensa");
        div.innerHTML = `🎁 ${R.titulo}`;
      } else {
        div.textContent = num;
      }
      if (num === posicao){
        const boneco = document.createElement("div");
        boneco.className = "boneco";
        boneco.textContent = "🧍";
        div.appendChild(boneco);
      }
      L.appendChild(div);
    });
    tabuleiro.appendChild(L);
  });
  document.getElementById("btnRecomecar").style.display = (posicao >= TOTAL_CASAS) ? "inline-flex" : "none";
}

function rolarDado(){
  const n = Math.floor(Math.random()*6) + 1;
  dadoEl.textContent = n;
  resNum.textContent = n;

  posicao += n;
  if (posicao >= TOTAL_CASAS) posicao = TOTAL_CASAS;

  const premio = recompensas.find(r => +r.posicao === posicao);
  if (premio){
    document.getElementById("textoRecompensa").textContent = `Você ganhou: ${premio.titulo}!`;
    abrirModal('ganhou');
  }
  desenharTabuleiro();
}

function recomecar(){
  posicao = 1;
  desenharTabuleiro();
}

function abrirModal(nome){
  document.getElementById("modal-"+nome).classList.add("show");
}
function fecharModal(nome){
  document.getElementById("modal-"+nome).classList.remove("show");
}

document.addEventListener("DOMContentLoaded", desenharTabuleiro);