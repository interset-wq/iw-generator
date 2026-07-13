// Header navigation icons - loaded after DOM is ready
function initNavIcons() {
    document.getElementById("pathHome")?.setAttribute("d", IconList["material/home-outline"]);
    document.getElementById("themeSwitch")?.setAttribute("d", IconList["material/brightness-7"]);
    document.getElementById("pathArchives")?.setAttribute("d", IconList["material/archive-outline"]);
    document.getElementById("pathCategories")?.setAttribute("d", IconList["material/folder-outline"]);
    document.getElementById("pathTags")?.setAttribute("d", IconList["material/tag-outline"]);
    document.getElementById("pathBack")?.setAttribute("d", IconList["material/home-outline"]);
}

function initPostListIcons() {
    const pinnedPosts = document.getElementsByClassName("svgTop1");
    const regularPosts = document.getElementsByClassName("svgTop0");
    for (let i = 0; i < pinnedPosts.length; i++) {
        pinnedPosts[i].setAttribute("d", IconList["material/push-pin"]);
        pinnedPosts[i].parentNode.style.color = "red";
    }
    for (let i = 0; i < regularPosts.length; i++) {
        regularPosts[i].setAttribute("d", IconList["material/article-outline"]);
    }
}

initNavIcons();
initPostListIcons();