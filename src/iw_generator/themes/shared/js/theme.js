/**
 * Theme toggle functionality.
 * Shared across all themes.
 */
(function() {
  var savedTheme = localStorage.getItem("meek_theme") || "light";
  document.documentElement.setAttribute("data-color-mode", savedTheme);

  var themeSettings = {
    "dark": ["dark", "material/brightness-4", "#00f0ff", "dark-blue"],
    "light": ["light", "material/brightness-7", "#ff5000", "github-light"],
    "auto": ["auto", "material/brightness-auto", "", "preferred-color-scheme"]
  };

  function changeTheme(mode, icon, color) {
    document.documentElement.setAttribute("data-color-mode", mode);
    var themeSwitch = document.getElementById("themeSwitch");
    if (themeSwitch) {
      themeSwitch.setAttribute("d", window.IconList ? window.IconList[icon] : "");
      themeSwitch.parentNode.style.color = color;
    }
  }

  window.modeSwitch = function() {
    var currentMode = document.documentElement.getAttribute("data-color-mode");
    var newMode = currentMode === "light" ? "dark" : currentMode === "dark" ? "auto" : "light";
    localStorage.setItem("meek_theme", newMode);
    if (themeSettings[newMode]) {
      changeTheme.apply(null, themeSettings[newMode]);
    }
  };

  if (themeSettings[savedTheme]) {
    changeTheme.apply(null, themeSettings[savedTheme]);
  }
})();
