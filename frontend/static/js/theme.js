const darkModeButton = document.getElementById("dark-mode")
const lightModeButton = document.getElementById("light-mode")

addEventListener("load", (event) => {
    localStorage_theme = localStorage.getItem("theme")
    setTheme(localStorage_theme || "light")
});

darkModeButton.addEventListener("click", (e) => {
    localStorage.setItem("theme", "dark")
    setTheme("dark")
})

lightModeButton.addEventListener("click", (e) => {
    localStorage.setItem("theme", "light")
    setTheme("light")
})

function setTheme(theme){
    if (theme === "dark") {
        document.documentElement.classList.add("dark")
    } else {
        document.documentElement.classList.remove("dark")
    }
}