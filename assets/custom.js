function scrollToBottom() {
  window.scrollTo(0, document.body.scrollHeight);
}

// Listen for changes to the 'data-content' attribute of the 'js-trigger' div
const trigger = document.getElementById("comment_section_p");
const observer = new MutationObserver(scrollToBottom);
observer.observe(trigger, { attributes: true, attributeFilter: ["innerText"] });
