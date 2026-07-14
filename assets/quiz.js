// Shared quiz widget — used by all lessons
// Usage: give each answer button class="option" and data-correct="true" on the right one
// Add a sibling .feedback div after each group of options

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.quiz-question').forEach(q => {
    const options = q.querySelectorAll('.option');
    const feedback = q.querySelector('.feedback');
    let answered = false;
    options.forEach(opt => {
      opt.addEventListener('click', () => {
        if (answered) return;
        answered = true;
        const correct = opt.dataset.correct === 'true';
        opt.classList.add(correct ? 'correct' : 'wrong');
        if (!correct) {
          options.forEach(o => { if (o.dataset.correct === 'true') o.classList.add('correct'); });
        }
        if (feedback) feedback.textContent = correct
          ? '✓ Correct — ' + (opt.dataset.explain || '')
          : '✗ Not quite — ' + (opt.dataset.explain || 'see the correct answer highlighted above.');
      });
    });
  });
});
