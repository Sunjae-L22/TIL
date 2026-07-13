/* ============================================================
   common.js — 모든 페이지가 공유하는 스크립트
   (i18n · 다크모드 · 네비 · 스크롤바 · 타임라인 · 모달 · 방명록 · 음악 · 이스터에그)
   ============================================================ */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------------- i18n dictionary ---------------- */
  var I18N = {
    ko: {
      "nav.home": "홈", "nav.projects": "프로젝트", "nav.about": "소개",
      /* index */
      "idx.h1": "데이터의 맥락을 이해하고,<br>최적의 모델을 구현합니다",
      "idx.lead": "고려대학교 빅데이터 사이언스 전공. 데이터 분석과 모델링, 자연어 처리까지 이어지는 실전형 역량으로 의미 있는 결과를 만듭니다.",
      "idx.cta.projects": "프로젝트 보기",
      "idx.cta.email": "이메일 보내기",
      "hl.title": "핵심 역량",
      "hl1.h": "데이터 분석 · 모델링 성과",
      "hl1.p": "환경부 공공데이터 활용 대회 최종 후보(Top 9), T-SUM 데이터 분석 경진대회 1위·2위 — 실전 데이터로 문제 해결 능력을 입증했습니다.",
      "hl2.h": "NLP · LLM 실전 경험",
      "hl2.p": "Llama-3-8B 편향성 평가, KoGPT2 파인튜닝, RAG 시스템 구축 등 최신 자연어 처리 아키텍처를 직접 다뤘습니다.",
      "hl3.h": "탄탄한 데이터 사이언스 기반",
      "hl3.p": "전공 평점 4.41/4.5, ADsP · SQLD · 빅데이터분석기사 자격을 보유하고 있습니다.",
      "stack.title": "기술 스택",
      "idx.cta2.h": "더 자세한 이야기가 궁금하다면",
      "idx.cta2.btn": "프로젝트 살펴보기",
      /* projects */
      "prj.title": "주요 프로젝트",
      "prj.lead": "편향성 분석부터 환경 데이터, 딥페이크 탐지까지 — 문제 정의와 검증 과정을 중심으로 정리했습니다.",
      "prj.view": "자세히 보기",
      "p.type.personal": "개인 프로젝트", "p.type.team": "팀 프로젝트",
      "p2.badge": "환경부 대회 · Top 9", "p3.badge": "T-SUM · 2위",
      "p1.sum": "LLM의 편향성을 수치화하고 모델 정렬(Alignment) 전후를 비교 분석",
      "p1.b1": "Meta-Llama-3-8B Base·Instruct 모델에 StereoSet을 적용해 젠더·인종·직업 등 도메인별 편향성 차이 측정",
      "p1.b2": "Bootstrap 기반 95% 신뢰구간 도출 등 통계적 방법론으로 정렬이 편향을 재구성하는 방식을 정량 검증",
      "p1.b3": "Hugging Face Transformers 기반의 재현 가능한 파이프라인 구축",
      "p2.sum": "조류·기후·대기오염 데이터를 통합한 환경 패널 데이터 구축 및 시계열 분석",
      "p2.b1": "3,616건의 조류 데이터와 Copernicus ERA5 기후·대기오염 데이터를 병합·전처리해 패널 데이터 구축",
      "p2.b2": "XGBoost + SHAP으로 해석 가능한 예측 모델링, 공간·시계열 클러스터링(DTW) 적용",
      "p2.b3": "이상치 탐지(Z-score)와 베이지안 What-if 시뮬레이션으로 취약 지역 도출",
      "p3.sum": "트랜스포머 기반 딥페이크 영상 탐지 파이프라인 구축",
      "p3.b1": "Video Swin Transformer와 CNN(Xception)+LSTM 베이스라인 성능 비교 분석 및 구현",
      "p3.b2": "얼굴 크롭·프레임 샘플링 전략과 클래스 불균형 대응으로 모델 안정성 향상",
      /* about */
      "ab.h1": "데이터로 배우고,<br>기록으로 증명합니다",
      "ab.lead": "통계에서 머신러닝, 자연어 처리까지 — 꾸준한 학습과 실전 프로젝트로 역량을 넓혀가고 있습니다.",
      "tl.title": "경력 · 학력",
      "tl1.h": "학부 연구생", "tl1.org": "고려대학교 세종캠퍼스 국가통계연구실",
      "tl1.b1": "SARIMAX 모델로 코로나19 확진자 수와 지역 간 인구 이동량의 상관관계 분석",
      "tl2.h": "고려대학교 세종캠퍼스", "tl2.org": "빅데이터 사이언스 학부",
      "tl2.b1": "<strong>전공 4.41 / 4.5</strong> · 전체 4.32 / 4.5",
      "tl2.b2": "기계학습, 다변량분석, 시계열분석, 딥러닝, 강화학습 등 이수",
      "tl2.date": "2020.03 — 2026.06 (졸업 예정)",
      "tl3.h": "Florida Atlantic University", "tl3.org": "교환학생 · College of Engineering & CS",
      "learn.title": "지속적인 학습",
      "learn1.h": "Technical Blog · 60+ posts",
      "learn1.p": "NLP·언어 모델·프롬프트 엔지니어링 중심의 논문 리뷰와 스터디 노트를 꾸준히 기록합니다.",
      "learn2.h": "자기주도 학습",
      "learn2.p": "Stanford CS224N을 이수했고, 『Effective Python』으로 파이썬 동작 원리를 매일 탐구하고 있습니다.",
      "travel.sub": "여행 블로그 미리보기",
      "travel.lead": "대전에서 플로리다까지 — 기록해 온, 그리고 기록할 순간들.",
      "tv1.p": "플로리다 애틀랜틱 대학교에서 보낸 한 학기의 기록.",
      "tv2.p": "SSAFY 16기 데이터 트랙 — 대전 캠퍼스 몰입기.",
      "tv3.p": "다음 여행을 준비 중입니다.",
      "travel.read": "블로그에서 읽기",
      "music.sub": "코딩할 때 듣는 무드",
      "music.desc": "Web Audio API로 실시간 생성되는 로파이 루프입니다. 음원 파일 없이, 브라우저가 직접 연주해요.",
      "music.play": "재생", "music.pause": "일시정지",
      "gb.title": "방명록",
      "gb.lead": "다녀간 흔적을 남겨주세요.",
      "gb.ph.name": "이름",
      "gb.ph.msg": "메시지를 남겨주세요",
      "gb.submit": "남기기",
      "gb.empty": "아직 방명록이 비어 있어요. 첫 번째 흔적을 남겨보세요!",
      "gb.note": "localStorage 데모 — 이 브라우저에만 저장됩니다.",
      "gb.delete": "삭제",
      "ft.rights": "© 2026 이선재 · Data Scientist",
      "ft.built": "HTML · Tailwind CSS · Vanilla JS로 직접 만들었습니다",
      "egg.badge": "🏆 히든 배지 획득! 로고를 7번 누르다니, 집요함 인정입니다.",
      "egg.ssafy": "🎓 SSAFY 코드 감지! 반갑습니다, 혹시 동기님?"
    },
    en: {
      "nav.home": "Home", "nav.projects": "Projects", "nav.about": "About",
      "idx.h1": "Understanding data in context,<br>building models that fit.",
      "idx.lead": "Big Data Science major at Korea University. I turn analysis, modeling, and NLP into results that matter.",
      "idx.cta.projects": "View projects",
      "idx.cta.email": "Get in touch",
      "hl.title": "Core Highlights",
      "hl1.h": "Proven results in data & modeling",
      "hl1.p": "Finalist (Top 9) in Korea's Ministry of Environment open-data competition, plus 1st & 2nd place at the T-SUM data analysis contest.",
      "hl2.h": "Hands-on NLP & LLMs",
      "hl2.p": "Bias evaluation on Llama-3-8B, KoGPT2 fine-tuning, and RAG systems — built and validated end to end.",
      "hl3.h": "A solid foundation",
      "hl3.p": "Major GPA 4.41/4.5 with ADsP, SQLD, and Big Data Analytics Engineer certifications.",
      "stack.title": "Tech Stack",
      "idx.cta2.h": "Want the full story?",
      "idx.cta2.btn": "Explore projects",
      "prj.title": "Key Projects",
      "prj.lead": "From LLM bias to environmental panels and deepfake detection — organized around problem framing and validation.",
      "prj.view": "View details",
      "p.type.personal": "Personal project", "p.type.team": "Team project",
      "p2.badge": "Ministry of Env. · Top 9", "p3.badge": "T-SUM · 2nd place",
      "p1.sum": "Quantifying intrinsic bias in LLMs, comparing before and after alignment.",
      "p1.b1": "Measured domain-wise bias (gender, race, profession) on Llama-3-8B Base vs Instruct using StereoSet",
      "p1.b2": "Bootstrap 95% confidence intervals to quantify how alignment reshapes bias",
      "p1.b3": "Reproducible pipeline built on Hugging Face Transformers",
      "p2.sum": "An environmental panel built from bird, climate, and air-pollution data, with time-series analysis.",
      "p2.b1": "Merged 3,616 bird records with Copernicus ERA5 climate and pollution data into a panel dataset",
      "p2.b2": "Interpretable modeling with XGBoost + SHAP; spatial and DTW time-series clustering",
      "p2.b3": "Z-score anomaly detection and Bayesian what-if scenarios to locate vulnerable regions",
      "p3.sum": "A transformer-based deepfake video detection pipeline.",
      "p3.b1": "Implemented and benchmarked Video Swin Transformer against an Xception+LSTM baseline",
      "p3.b2": "Face cropping, frame-sampling strategy, and class-imbalance handling for model stability",
      "ab.h1": "Learning with data,<br>proving with records.",
      "ab.lead": "From statistics to machine learning and NLP — growing through steady study and real projects.",
      "tl.title": "Experience & Education",
      "tl1.h": "Undergraduate Research Assistant", "tl1.org": "National Statistics Lab, Korea University Sejong",
      "tl1.b1": "Modeled the relationship between COVID-19 cases and inter-regional mobility with SARIMAX",
      "tl2.h": "Korea University, Sejong Campus", "tl2.org": "B.S. in Big Data Science",
      "tl2.b1": "<strong>Major GPA 4.41 / 4.5</strong> · Cumulative 4.32 / 4.5",
      "tl2.b2": "Coursework: ML, multivariate analysis, time series, deep learning, RL",
      "tl2.date": "2020.03 — 2026.06 (expected)",
      "tl3.h": "Florida Atlantic University", "tl3.org": "Exchange student · College of Engineering & CS",
      "learn.title": "Continuous Learning",
      "learn1.h": "Technical Blog · 60+ posts",
      "learn1.p": "Ongoing paper reviews and study notes on NLP, language models, and prompt engineering.",
      "learn2.h": "Self-directed study",
      "learn2.p": "Completed Stanford CS224N; digging into Python internals daily with Effective Python.",
      "travel.sub": "Travel blog, previewed",
      "travel.lead": "From Daejeon to Florida — moments logged, and moments to come.",
      "tv1.p": "One semester at Florida Atlantic University.",
      "tv2.p": "SSAFY 16th cohort, Data Track — deep-diving at the Daejeon campus.",
      "tv3.p": "Next trip loading…",
      "travel.read": "Read on the blog",
      "music.sub": "What coding sounds like",
      "music.desc": "A lo-fi loop generated in real time with the Web Audio API — no audio files, your browser plays it live.",
      "music.play": "Play", "music.pause": "Pause",
      "gb.title": "Guestbook",
      "gb.lead": "Leave a note that you were here.",
      "gb.ph.name": "Name",
      "gb.ph.msg": "Write a message",
      "gb.submit": "Sign",
      "gb.empty": "The book is empty — be the first to sign!",
      "gb.note": "localStorage demo — saved only in this browser.",
      "gb.delete": "Delete",
      "ft.rights": "© 2026 Sunjae Lee · Data Scientist",
      "ft.built": "Hand-built with HTML, Tailwind CSS & vanilla JS",
      "egg.badge": "🏆 Hidden badge unlocked — seven clicks of pure persistence.",
      "egg.ssafy": "🎓 SSAFY code detected! Hello, classmate?"
    }
  };

  var lang = "ko";
  try { lang = localStorage.getItem("lang") || "ko"; } catch (e) {}
  if (!I18N[lang]) lang = "ko";

  function applyLang(next) {
    lang = next;
    var dict = I18N[lang];
    $$("[data-i18n]").forEach(function (el) {
      var v = dict[el.getAttribute("data-i18n")];
      if (v !== undefined) el.innerHTML = v;
    });
    $$("[data-i18n-ph]").forEach(function (el) {
      var v = dict[el.getAttribute("data-i18n-ph")];
      if (v !== undefined) el.setAttribute("placeholder", v);
    });
    document.documentElement.lang = lang;
    var lt = $("#lang-toggle");
    if (lt) lt.textContent = lang === "ko" ? "EN" : "한";
    try { localStorage.setItem("lang", lang); } catch (e) {}
    renderGuestbook(); // 날짜 포맷 갱신
    document.dispatchEvent(new CustomEvent("langchange"));
  }

  /* ---------------- theme (dark mode) ---------------- */
  function applyTheme(t) {
    document.documentElement.classList.toggle("dark", t === "dark");
    var tt = $("#theme-toggle");
    if (tt) tt.textContent = t === "dark" ? "☀" : "☾";
    try { localStorage.setItem("theme", t); } catch (e) {}
  }

  /* ---------------- nav: 현재 페이지 표시 + 햄버거 ---------------- */
  function initNav() {
    var page = document.body.dataset.page;
    $$("a[data-page]").forEach(function (a) {
      if (a.dataset.page === page) {
        a.classList.add("text-white", "font-semibold");
        a.setAttribute("aria-current", "page");
      } else {
        a.classList.add("text-white/60", "hover:text-white");
      }
    });
    var toggle = $("#nav-toggle"), menu = $("#mobile-menu");
    if (toggle && menu) {
      toggle.addEventListener("click", function () {
        var open = menu.classList.toggle("hidden");
        toggle.setAttribute("aria-expanded", String(!open));
      });
    }
  }

  /* ---------------- scroll progress bar ---------------- */
  function initProgress() {
    var bar = $("#progress");
    if (!bar) return;
    var onScroll = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------------- reveal on scroll ---------------- */
  function initReveal() {
    var items = $$(".reveal");
    if (!("IntersectionObserver" in window)) { items.forEach(function (el) { el.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------------- interactive timeline (about) ---------------- */
  function initTimeline() {
    var tl = $("#timeline"), fill = $("#tl-fill");
    if (!tl || !fill) return;
    var dots = $$(".tl-dot", tl);
    var onScroll = function () {
      var r = tl.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, (window.innerHeight * 0.6 - r.top) / r.height));
      fill.style.height = p * 100 + "%";
      var lineY = window.innerHeight * 0.6;
      dots.forEach(function (d) { d.classList.toggle("on", d.getBoundingClientRect().top < lineY); });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------------- project detail modal (projects) ---------------- */
  function initModal() {
    var modal = $("#modal");
    if (!modal) return;
    var mImg = $("#modal-img"), mMeta = $("#modal-meta"), mTitle = $("#modal-title"),
        mSum = $("#modal-summary"), mList = $("#modal-list"), mClose = $("#modal-close"),
        lastFocus = null;

    function open(card) {
      lastFocus = card;
      mImg.src = card.getAttribute("data-thumb");
      var img = $(".p-thumb img", card);
      mImg.alt = img ? img.alt : "";
      mMeta.innerHTML = "";
      $$(".p-meta-item", card).forEach(function (s) { mMeta.appendChild(s.cloneNode(true)); });
      mTitle.textContent = $("h3", card).textContent;
      mSum.textContent = $(".p-sum", card).textContent;
      mList.innerHTML = $(".p-bullets", card).innerHTML;
      modal.classList.remove("invisible", "opacity-0");
      modal.setAttribute("aria-hidden", "false");
      $(".panel", modal).classList.remove("translate-y-4", "scale-95");
      document.body.style.overflow = "hidden";
      mClose.focus();
    }
    function close() {
      modal.classList.add("invisible", "opacity-0");
      modal.setAttribute("aria-hidden", "true");
      $(".panel", modal).classList.add("translate-y-4", "scale-95");
      document.body.style.overflow = "";
      if (lastFocus) lastFocus.focus();
    }
    $$(".project").forEach(function (card) {
      card.addEventListener("click", function () { open(card); });
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(card); }
      });
    });
    mClose.addEventListener("click", close);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.getAttribute("aria-hidden") === "false") close();
    });
  }

  /* ---------------- guestbook (about, localStorage) ---------------- */
  var GB_KEY = "guestbook.v1";
  function gbLoad() { try { return JSON.parse(localStorage.getItem(GB_KEY)) || []; } catch (e) { return []; } }
  function gbSave(list) { try { localStorage.setItem(GB_KEY, JSON.stringify(list)); } catch (e) {} }

  function renderGuestbook() {
    var listEl = $("#gb-list");
    if (!listEl) return;
    var dict = I18N[lang], entries = gbLoad();
    listEl.innerHTML = "";
    if (!entries.length) {
      var empty = document.createElement("li");
      empty.className = "rounded-[18px] border border-dashed border-hair p-6 text-center text-[15px] text-mut dark:border-white/15 dark:text-mutd";
      empty.textContent = dict["gb.empty"];
      listEl.appendChild(empty);
      return;
    }
    entries.forEach(function (en, i) {
      var li = document.createElement("li");
      li.className = "rounded-[18px] border border-hair bg-white p-5 dark:border-white/10 dark:bg-[#1d1d1f]";
      var head = document.createElement("div");
      head.className = "mb-2 flex items-baseline justify-between gap-3";
      var name = document.createElement("strong");
      name.className = "text-[15px] font-semibold text-ink dark:text-white";
      name.textContent = en.n;
      var right = document.createElement("span");
      right.className = "flex items-center gap-3 text-[12px] text-mut dark:text-mutd";
      var date = document.createElement("span");
      date.textContent = new Date(en.t).toLocaleDateString(lang === "en" ? "en-US" : "ko-KR", { year: "numeric", month: "short", day: "numeric" });
      var del = document.createElement("button");
      del.className = "transition hover:text-ab dark:hover:text-ab-dk";
      del.textContent = I18N[lang]["gb.delete"];
      del.addEventListener("click", function () {
        var list = gbLoad(); list.splice(i, 1); gbSave(list); renderGuestbook();
      });
      right.appendChild(date); right.appendChild(del);
      head.appendChild(name); head.appendChild(right);
      var msg = document.createElement("p");
      msg.className = "text-[15px] leading-[1.47] tracking-[-0.2px] text-ink/80 dark:text-white/80";
      msg.textContent = en.m;
      li.appendChild(head); li.appendChild(msg);
      listEl.appendChild(li);
    });
  }

  function initGuestbook() {
    var nameIn = $("#gb-name"), msgIn = $("#gb-msg"), btn = $("#gb-submit");
    if (!nameIn || !msgIn || !btn) return;
    function submit() {
      var n = nameIn.value.trim(), m = msgIn.value.trim();
      if (!n || !m) { (n ? msgIn : nameIn).focus(); return; }
      var list = gbLoad();
      list.unshift({ n: n.slice(0, 20), m: m.slice(0, 200), t: Date.now() });
      gbSave(list.slice(0, 30));
      nameIn.value = ""; msgIn.value = "";
      renderGuestbook();
    }
    btn.addEventListener("click", submit);
    msgIn.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } });
    renderGuestbook();
  }

  /* ---------------- generative lo-fi player (about) ---------------- */
  function initMusic() {
    var btn = $("#music-btn"), canvas = $("#music-viz");
    if (!btn || !canvas) return;
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { btn.disabled = true; return; }

    var ac = null, master = null, analyser = null, noiseSrc = null;
    var playing = false, nextT = 0, step = 0, timer = null, raf = null;
    // F△7 → Em7 → Dm7 → C△7 (72 BPM, 4박 = 3.33s)
    var CHORDS = [
      { bass: 87.31, notes: [174.61, 220.0, 261.63, 329.63] },
      { bass: 82.41, notes: [164.81, 196.0, 246.94, 293.66] },
      { bass: 73.42, notes: [146.83, 174.61, 220.0, 261.63] },
      { bass: 65.41, notes: [130.81, 164.81, 196.0, 246.94] }
    ];
    var DUR = 3.33;

    function setup() {
      ac = new AC();
      master = ac.createGain(); master.gain.value = 0.9;
      analyser = ac.createAnalyser(); analyser.fftSize = 64;
      master.connect(analyser); analyser.connect(ac.destination);
      // 은은한 vinyl noise
      var len = ac.sampleRate * 2, buf = ac.createBuffer(1, len, ac.sampleRate);
      var d = buf.getChannelData(0);
      for (var i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      noiseSrc = ac.createBufferSource(); noiseSrc.buffer = buf; noiseSrc.loop = true;
      var nf = ac.createBiquadFilter(); nf.type = "lowpass"; nf.frequency.value = 450;
      var ng = ac.createGain(); ng.gain.value = 0.012;
      noiseSrc.connect(nf); nf.connect(ng); ng.connect(master);
      noiseSrc.start();
    }

    function playChord(ch, t) {
      var lp = ac.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 1100; lp.Q.value = 0.7;
      lp.connect(master);
      ch.notes.forEach(function (f, i) {
        var o = ac.createOscillator(), g = ac.createGain();
        o.type = "triangle"; o.frequency.value = f;
        o.detune.value = (Math.random() - 0.5) * 8; // lo-fi 흔들림
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(0.055, t + 0.35 + i * 0.04);
        g.gain.setValueAtTime(0.055, t + DUR - 0.9);
        g.gain.linearRampToValueAtTime(0, t + DUR - 0.05);
        o.connect(g); g.connect(lp);
        o.start(t); o.stop(t + DUR);
      });
      var b = ac.createOscillator(), bg = ac.createGain();
      b.type = "sine"; b.frequency.value = ch.bass;
      bg.gain.setValueAtTime(0, t);
      bg.gain.linearRampToValueAtTime(0.10, t + 0.15);
      bg.gain.linearRampToValueAtTime(0, t + DUR - 0.1);
      b.connect(bg); bg.connect(master);
      b.start(t); b.stop(t + DUR);
    }

    function schedule() {
      while (nextT < ac.currentTime + 0.3) {
        playChord(CHORDS[step % CHORDS.length], Math.max(nextT, ac.currentTime + 0.02));
        nextT += DUR; step++;
      }
    }

    function draw() {
      var ctx = canvas.getContext("2d");
      var data = new Uint8Array(analyser.frequencyBinCount);
      var loop = function () {
        if (!playing) return;
        analyser.getByteFrequencyData(data);
        var W = canvas.width, H = canvas.height, n = 22, gap = 5;
        var bw = (W - gap * (n - 1)) / n;
        ctx.clearRect(0, 0, W, H);
        ctx.fillStyle = "#2997ff";
        for (var i = 0; i < n; i++) {
          var v = data[i + 2] / 255;
          var h = Math.max(3, v * H * 0.95);
          ctx.globalAlpha = 0.35 + v * 0.65;
          ctx.beginPath();
          if (ctx.roundRect) ctx.roundRect(i * (bw + gap), H - h, bw, h, 3); else ctx.rect(i * (bw + gap), H - h, bw, h);
          ctx.fill();
        }
        raf = requestAnimationFrame(loop);
      };
      raf = requestAnimationFrame(loop);
    }

    function setLabel() {
      var l = $("#music-label");
      if (l) l.textContent = I18N[lang][playing ? "music.pause" : "music.play"];
      var ic = $("#music-icon");
      if (ic) ic.textContent = playing ? "❚❚" : "▶";
    }

    btn.addEventListener("click", function () {
      if (!ac) { try { setup(); } catch (e) { btn.disabled = true; return; } }
      if (!playing) {
        ac.resume().then(function () {
          playing = true; nextT = ac.currentTime + 0.05;
          schedule(); timer = setInterval(schedule, 200);
          draw(); setLabel();
        });
      } else {
        playing = false;
        clearInterval(timer); if (raf) cancelAnimationFrame(raf);
        ac.suspend(); setLabel();
      }
    });
    document.addEventListener("langchange", setLabel);
    setLabel();
  }

  /* ---------------- easter eggs ---------------- */
  function toast(msg) {
    var t = document.createElement("div");
    t.className = "toast"; t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.classList.add("show"); });
    setTimeout(function () { t.classList.remove("show"); setTimeout(function () { t.remove(); }, 350); }, 3200);
  }
  function initEggs() {
    // 1) 로고 7연타 → 히든 배지 (1~2회 클릭은 정상적으로 홈 이동, 카운트는 sessionStorage로 유지)
    var brand = $("#brand"), unlocked = false;
    try { unlocked = localStorage.getItem("egg.badge") === "1"; } catch (e) {}
    var star = $("#brand-star");
    if (unlocked && star) star.classList.remove("hidden");
    if (brand) brand.addEventListener("click", function (e) {
      var n = 0, t = 0, now = Date.now();
      try {
        n = parseInt(sessionStorage.getItem("egg.n") || "0", 10);
        t = parseInt(sessionStorage.getItem("egg.t") || "0", 10);
      } catch (err) {}
      n = (now - t < 4000) ? n + 1 : 1;
      try { sessionStorage.setItem("egg.n", String(n)); sessionStorage.setItem("egg.t", String(now)); } catch (err) {}
      if (n >= 3) e.preventDefault(); // 연타 구간에서는 이동 방지
      if (n >= 7) {
        try { sessionStorage.removeItem("egg.n"); } catch (err) {}
        toast(I18N[lang]["egg.badge"]);
        try { localStorage.setItem("egg.badge", "1"); } catch (err) {}
        if (star) star.classList.remove("hidden");
      }
    });
    // 2) 아무 곳에서나 's-s-a-f-y' 타이핑
    var buf = "";
    document.addEventListener("keydown", function (e) {
      if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
      buf = (buf + e.key.toLowerCase()).slice(-5);
      if (buf === "ssafy") { toast(I18N[lang]["egg.ssafy"]); buf = ""; }
    });
    // 3) 콘솔 메시지
    try {
      console.log("%c SUNJAE LEE %c data scientist · nlp / llm ",
        "background:#0066cc;color:#fff;padding:4px 8px;border-radius:6px 0 0 6px;font-weight:700",
        "background:#1d1d1f;color:#2997ff;padding:4px 8px;border-radius:0 6px 6px 0");
      console.log("여기까지 열어보셨다면… 같이 일해요 → leeseonjae0111@gmail.com");
    } catch (e) {}
  }

  /* ---------------- boot ---------------- */
  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initProgress();
    initModal();
    initGuestbook();
    initTimeline();
    initMusic();
    initEggs();
    applyLang(lang);   // 방명록 렌더 포함
    initReveal();

    var themeBtn = $("#theme-toggle");
    applyTheme(document.documentElement.classList.contains("dark") ? "dark" : "light");
    if (themeBtn) themeBtn.addEventListener("click", function () {
      applyTheme(document.documentElement.classList.contains("dark") ? "light" : "dark");
    });
    var langBtn = $("#lang-toggle");
    if (langBtn) langBtn.addEventListener("click", function () {
      applyLang(lang === "ko" ? "en" : "ko");
    });
  });
})();
