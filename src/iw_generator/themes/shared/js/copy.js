/**
 * Copy button functionality for code blocks.
 * Shared across all themes.
 *
 * Naming: .iw-code__copy
 */
document.addEventListener('click', function(e) {
  var btn = e.target.closest('.iw-code__copy');
  if (!btn) return;
  var codeBlock = btn.closest('.iw-code');
  if (!codeBlock) return;
  var code = codeBlock.querySelector('code');
  if (!code) return;
  navigator.clipboard.writeText(code.textContent).then(function() {
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
    setTimeout(function() {
      btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>';
    }, 2000);
  });
});
