/*
*  Title: Night City script
*  Description: HUD menu, typed roles, parallax, scroll reveal and a little cheat code
*/
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("js");

  // Footer year
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  // HUD: mobile toggle + solid background after scrolling
  var hud = document.getElementById("hud");
  var toggle = document.getElementById("hud-toggle");
  var menu = document.getElementById("hud-menu");

  toggle.addEventListener("click", function () {
    var open = menu.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  menu.addEventListener("click", function (e) {
    if (e.target.tagName === "A") {
      menu.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  // Highlight the HUD link of the section on screen
  var links = {};
  menu.querySelectorAll("a").forEach(function (a) {
    links[a.getAttribute("href").slice(1)] = a;
  });
  if ("IntersectionObserver" in window) {
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        Object.keys(links).forEach(function (id) {
          links[id].classList.toggle("active", id === entry.target.id);
        });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(links).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) sectionObserver.observe(el);
    });

    // Reveal blocks as they scroll into view
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll(".reveal").forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("in");
    });
  }

  // Parallax on the hero layers
  var layers = document.querySelectorAll(".layer");
  var hero = document.getElementById("top");
  var ticking = false;

  function onScroll() {
    var y = window.scrollY;
    hud.classList.toggle("scrolled", y > 40);
    if (!reduceMotion && y < hero.offsetHeight) {
      layers.forEach(function (layer) {
        layer.style.transform = "translate3d(0," + Math.round(y * layer.dataset.depth) + "px,0)";
      });
    }
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(onScroll);
    }
  }, { passive: true });
  onScroll();

  // Hero prompt: type "whoami" like a real shell
  var cmd = document.getElementById("cmd");
  if (cmd && !reduceMotion) {
    var command = cmd.textContent;
    cmd.textContent = "";
    var typeCmd = function (i) {
      cmd.textContent = command.slice(0, i);
      if (i < command.length) setTimeout(function () { typeCmd(i + 1); }, 110 + Math.random() * 90);
    };
    setTimeout(function () { typeCmd(1); }, 700);
  }

  // Typed roles in the hero
  var typed = document.getElementById("typed");
  var roles = [
    "Security Transformation Analyst",
    "Computer Engineer",
    "Ethical Hacker",
    "MSc Cyber Security Student"
  ];
  if (typed && !reduceMotion) {
    var roleIndex = 0;
    var charIndex = roles[0].length;
    var deleting = true;
    var tick = function () {
      var word = roles[roleIndex];
      if (deleting) {
        charIndex--;
        if (charIndex === 0) {
          deleting = false;
          roleIndex = (roleIndex + 1) % roles.length;
        }
      } else {
        charIndex++;
      }
      typed.textContent = roles[roleIndex].slice(0, charIndex);
      var delay = deleting ? 35 : 75;
      if (!deleting && charIndex === roles[roleIndex].length) {
        deleting = true;
        delay = 2200;
      }
      setTimeout(tick, delay);
    };
    setTimeout(tick, 2600);
  }

  // Konami code easter egg
  var toast = document.getElementById("toast");
  var code = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"];
  var pos = 0;
  var toastTimer;
  window.addEventListener("keydown", function (e) {
    var key = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    pos = key === code[pos] ? pos + 1 : (key === code[0] ? 1 : 0);
    if (pos === code.length) {
      pos = 0;
      var on = document.body.classList.toggle("cheat");
      toast.textContent = on ? "CHEAT ENABLED: +30 LIVES" : "CHEAT DISABLED";
      toast.classList.add("show");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function () {
        toast.classList.remove("show");
      }, 2600);
    }
  });
})();
