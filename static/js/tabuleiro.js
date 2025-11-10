document.addEventListener("DOMContentLoaded", () => {
  const elTabuleiro = document.getElementById("tabuleiro");
  const dadoEl = document.getElementById("dado");
  const resNum = document.getElementById("res-num");
  const btnRecomecar = document.getElementById("btnRecomecar");
  if (!elTabuleiro) return;

  elTabuleiro.removeAttribute("style");

  const TOTAL_CASAS = Number(elTabuleiro.dataset.totalCasas) || 100;
  const CASAS_POR_LINHA = Number(elTabuleiro.dataset.porLinha) || 10;
  const nomeJogador = (elTabuleiro.dataset.username || window.nomeJogador || "Jogador").trim();

  const RAW = Array.isArray(window.recompensas) ? window.recompensas : [];
  const RECOMPENSAS = new Map(
    RAW.map(r => {
      const pos = Number(r?.posicao ?? r?.casa ?? r?.pos ?? r?.numero);
      return { ...r, posicao: Number.isFinite(pos) ? pos : null };
    })
    .filter(r => r.posicao && r.posicao >= 1 && r.posicao <= TOTAL_CASAS)
    .map(r => [r.posicao, r])
  );

  let posicao = 1;

  function gerarLinhas(total, porLinha) {
    const linhas = [];
    let atual = 1;
    const tot = Math.ceil(total / porLinha);
    for (let i = 0; i < tot; i++) {
      const linha = [];
      for (let j = 0; j < porLinha && atual <= total; j++) linha.push(atual++);
      if (i % 2 === 1) linha.reverse();
      linhas.push(linha);
    }
    return linhas;
  }
  const LINHAS = gerarLinhas(TOTAL_CASAS, CASAS_POR_LINHA);

  function desenharTabuleiro() {
    elTabuleiro.innerHTML = "";
    LINHAS.forEach((nums, idx) => {
      const faixa = document.createElement("div");
      faixa.className = "linha";
      if (idx % 2 === 1) faixa.classList.add("invertida");

      nums.forEach(i => {
        const casa = document.createElement("div");
        casa.className = "casa";
        if (i === 1) casa.classList.add("casa-start");
        if (i === TOTAL_CASAS) casa.classList.add("casa-finish");

        casa.innerHTML = `<span class="num">${i}</span>`;

        if (RECOMPENSAS.has(i)) {
          const r = RECOMPENSAS.get(i);
          casa.classList.add("recompensa");
          const wrap = document.createElement("div");
          wrap.className = "rec";
          wrap.innerHTML = `<span class="gift">🎁</span><span class="rec-nome">${r.titulo || "Recompensa"}</span>`;
          casa.appendChild(wrap);
          casa.title = r.titulo || "Recompensa";
        }

        if (i === posicao) {
          const boneco = document.createElement("div");
          boneco.className = "boneco";
          boneco.textContent = "🧍";
          const nome = document.createElement("div");
          nome.className = "nome-jogador";
          nome.textContent = nomeJogador;
          casa.appendChild(boneco);
          casa.appendChild(nome);
        }

        faixa.appendChild(casa);
      });

      elTabuleiro.appendChild(faixa);
    });

    if (btnRecomecar)
      btnRecomecar.style.display = posicao >= TOTAL_CASAS ? "inline-flex" : "none";
  }

  desenharTabuleiro();

  window.rolarDado = function () {
    const n = Math.floor(Math.random() * 6) + 1;
    if (dadoEl) dadoEl.textContent = n;
    if (resNum) resNum.textContent = n;

    posicao += n;
    if (posicao > TOTAL_CASAS) posicao = TOTAL_CASAS;

    if (RECOMPENSAS.has(posicao)) {
      const premio = RECOMPENSAS.get(posicao);
      const el = document.getElementById("textoRecompensa");
      if (el) el.textContent = `Você ganhou: ${premio.titulo || "Recompensa"}!`;
      abrirModal("ganhou");
      fireConfetti(2000, 200);
    }

    if (posicao === TOTAL_CASAS) {
      const el = document.getElementById("textoRecompensa");
      if (el) el.textContent = "🎯 Você concluiu o tabuleiro!";
      abrirModal("ganhou");
      fireConfetti(2500, 260);
    }

    desenharTabuleiro();
  };

  window.recomecar = function () {
    posicao = 1;
    desenharTabuleiro();
    removeConfettiIfAny();
  };

  // ----- Modal -----
  let escHandler = null;
  function backdropClose(e) {
    if (e.target.classList.contains("modal"))
      fecharModal(e.target.id.replace("modal-",""));
  }

  window.abrirModal = function (nome) {
    const m = document.getElementById("modal-" + nome);
    if (!m) return;
    if (m.parentElement !== document.body) document.body.appendChild(m); // garante overlay full
    m.classList.add("show");
    document.body.classList.add("modal-open");
    m.addEventListener("click", backdropClose);
    escHandler = e => e.key === "Escape" && fecharModal(nome);
    document.addEventListener("keydown", escHandler);
  };

  window.fecharModal = function (nome) {
    const m = document.getElementById("modal-" + nome);
    if (!m) return;
    m.classList.remove("show");
    document.body.classList.remove("modal-open");
    m.removeEventListener("click", backdropClose);
    if (escHandler) { document.removeEventListener("keydown", escHandler); escHandler = null; }
    removeConfettiIfAny();
  };

  // ----- Confete -----
  function fireConfetti(durationMs = 2000, count = 200) {
    removeConfettiIfAny();

    const c = document.createElement("canvas");
    c.id = "confetti-canvas";
    c.style.position = "fixed";
    c.style.inset = "0";
    c.style.pointerEvents = "none";
    c.style.zIndex = "10001";
    document.body.appendChild(c);

    const ctx = c.getContext("2d");
    const DPR = Math.max(1, window.devicePixelRatio || 1);
    function resize() {
      c.width = Math.floor(window.innerWidth * DPR);
      c.height = Math.floor(window.innerHeight * DPR);
      ctx.setTransform(1,0,0,1,0,0);
      ctx.scale(DPR, DPR);
    }
    resize();
    const onResize = () => resize();
    window.addEventListener("resize", onResize);

    const colors = ["#ff4757","#ffa502","#2ed573","#1e90ff","#a55eea","#ffdd59"];
    const parts = Array.from({ length: count }).map(() => ({
      x: Math.random() * window.innerWidth,
      y: -20 + Math.random() * 40,
      r: 4 + Math.random() * 6,
      c: colors[(Math.random() * colors.length) | 0],
      vx: -3 + Math.random() * 6,
      vy: 4 + Math.random() * 3,
      g: 0.12 + Math.random() * 0.25,
      a: 1,
      spin: (Math.random() * 2 - 1) * 0.2,
      ang: Math.random() * Math.PI * 2
    }));

    const start = performance.now();
    function frame(now) {
      const t = now - start;
      ctx.clearRect(0, 0, c.width, c.height);
      parts.forEach(p => {
        p.vy += p.g;
        p.x += p.vx;
        p.y += p.vy;
        p.ang += p.spin;
        p.a = 1 - t / durationMs;

        ctx.save();
        ctx.globalAlpha = Math.max(0, p.a);
        ctx.translate(p.x, p.y);
        ctx.rotate(p.ang);
        ctx.fillStyle = p.c;
        ctx.fillRect(-p.r, -p.r, p.r * 2, p.r * 2);
        ctx.restore();
      });

      if (t < durationMs) requestAnimationFrame(frame);
      else {
        window.removeEventListener("resize", onResize);
        c.remove();
      }
    }
    requestAnimationFrame(frame);
  }

  function removeConfettiIfAny() {
    const c = document.getElementById("confetti-canvas");
    if (c) c.remove();
  }
});
