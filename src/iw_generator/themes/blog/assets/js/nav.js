// Header navigation icons - loaded after DOM is ready
function initNavIcons() {
    document.getElementById("pathHome")?.setAttribute("d", IconList["material/home-outline"]);
    document.getElementById("themeSwitch")?.setAttribute("d", IconList["material/brightness-7"]);
    document.getElementById("pathArchives")?.setAttribute("d", IconList["material/archive-outline"]);
    document.getElementById("pathCategories")?.setAttribute("d", IconList["material/folder-outline"]);
    document.getElementById("pathTags")?.setAttribute("d", IconList["material/tag-outline"]);
    document.getElementById("pathSearch")?.setAttribute("d", IconList["material/magnify"]);
    document.getElementById("pathBack")?.setAttribute("d", IconList["material/arrow-left"]);
}

initNavIcons();