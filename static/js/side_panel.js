function toggleSidebar() {
    const side_panel = document.getElementById('side-panel');
    side_panel.classList.toggle('show');
    document.body.classList.toggle('side-panel-open');
    console.log("Toggle!");
}