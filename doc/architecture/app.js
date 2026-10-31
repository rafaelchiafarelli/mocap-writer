// clickable diagram boxes: each <g class="box" data-k="..."> shows
// window.BOXES[k] (title, what, files, hands) in #detail
(function () {
  function show(k) {
    var d = (window.BOXES || {})[k];
    var el = document.getElementById("detail");
    if (!d || !el) return;
    document.querySelectorAll(".box").forEach(function (b) { b.classList.toggle("on", b.dataset.k === k); });
    el.innerHTML = "<h3></h3><dl><dt>What it is</dt><dd class='w'></dd><dt>Files</dt><dd class='f'></dd><dt>Hands to</dt><dd class='h'></dd></dl>";
    el.querySelector("h3").textContent = d.title;
    el.querySelector(".w").innerHTML = d.what;
    el.querySelector(".f").innerHTML = d.files;
    el.querySelector(".h").innerHTML = d.hands;
  }
  document.querySelectorAll(".box").forEach(function (b) {
    b.setAttribute("tabindex", "0");
    b.setAttribute("role", "button");
    b.addEventListener("click", function () { show(b.dataset.k); });
    b.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); show(b.dataset.k); } });
  });
  var first = document.querySelector(".box");
  if (first) show(first.dataset.k);
  document.querySelectorAll("[data-reveal]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var t = document.getElementById(btn.dataset.reveal);
      t.hidden = !t.hidden;
      btn.textContent = t.hidden ? "Show the answer" : "Hide the answer";
    });
  });
})();
