function shortcuts(e) {
    if (e.key == "s" && e.metaKey === true) {
        document.getElementById("my_btn").click();
    };
    //else {
    //    alert(e.code);
    //    }
}
document.addEventListener('keyup', shortcuts, false);