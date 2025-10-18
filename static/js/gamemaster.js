
window.ishost = 1;
window.playerName = "Gamemaster"

function msg_host_join() {
  console.log(JSON.stringify({
    cmd: "join",
    host: true,
    name: "Gamemaster"
  }))
  return JSON.stringify({
    cmd: "join",
    host: true,
    name: "Gamemaster"
  });
}

window.addEventListener("wsConnected", (event) => {
  window.ws.send(msg_host_join());
});

function startGame() {

}

let currentQuestion = null; // store the selected question

function refreshQuestionList() {
  fetch(`${window.location.origin}/api/questions`)
    .then(r => r.json())
    .then(data => {
      const qlist = document.getElementById("questionList");
      qlist.innerHTML = "";

      data.forEach(q => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.innerHTML = `<strong>${q.title} ${q.seen === true ? '<span class="badge text-bg-warning">Seen</span>' : ''}</strong><ul class="answers-list">
    A: ${q.ans_a}${q.correct_ans === 0 ? ' <span class="badge text-bg-success">✓</span>' : ''}<br>
    B: ${q.ans_b}${q.correct_ans === 1 ? ' <span class="badge text-bg-success">✓</span>' : ''}<br>
    C: ${q.ans_c}${q.correct_ans === 2 ? ' <span class="badge text-bg-success">✓</span>' : ''}<br>
    D: ${q.ans_d}${q.correct_ans === 3 ? ' <span class="badge text-bg-success">✓</span>' : ''}<br>
    </ul>`;
        li.addEventListener("click", () => openQuestionModal(q));
        qlist.appendChild(li);
      });
    })
    .catch(err => console.error(err));
}

function openQuestionModal(q) {
  currentQuestion = q; // store the question globally for edit/delete

  document.getElementById("modalTitle").textContent = q.title;

  const answersList = document.getElementById("modalAnswers");
  answersList.innerHTML = "";
  ["ans_a", "ans_b", "ans_c", "ans_d"].forEach((key, i) => {
    const li = document.createElement("li");
    li.textContent = q[key];
    if (i === q.correct_ans) li.style.fontWeight = "bold";
    answersList.appendChild(li);
  });

  document.getElementById("modalCorrect").textContent = ["A", "B", "C", "D"][q.correct_ans] || "-";
  document.getElementById("modalFactoid").textContent = q.factoid || "-";

  const modalEl = document.getElementById('questionModal');
  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

// Example Edit & Delete handlers
document.getElementById("editQuestionBtn").addEventListener("click", () => {
  if (!currentQuestion) return;
  // Here you could populate your "New Question" modal for editing
  alert("Edit question: " + currentQuestion.title);
});

document.getElementById("deleteQuestionBtn").addEventListener("click", async () => {
  if (!currentQuestion) return;
  if (!confirm("Are you sure you want to delete this question?")) return;

  try {
    const res = await fetch(`${window.location.origin}/api/questions/${currentQuestion.id}`, {
      method: "DELETE"
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    alert("Question deleted!");
    const modalEl = document.getElementById('questionModal');
    bootstrap.Modal.getInstance(modalEl).hide();
    refreshQuestionList();
  } catch (err) {
    console.error(err);
    alert("Failed to delete question.");
  }
});

document.getElementById("editQuestionBtn").addEventListener("click", () => {
  if (!currentQuestion) return;

  const form = document.getElementById('newQuestionForm');

  // Fill in form fields
  form.querySelector('#question_id').value = currentQuestion.id;
  form.querySelector('input[name="nq-title"]').value = currentQuestion.title;
  form.querySelector('input[name="nq-a"]').value = currentQuestion.ans_a;
  form.querySelector('input[name="nq-b"]').value = currentQuestion.ans_b;
  form.querySelector('input[name="nq-c"]').value = currentQuestion.ans_c;
  form.querySelector('input[name="nq-d"]').value = currentQuestion.ans_d;
  form.querySelector('textarea[name="factoid"]').value = currentQuestion.factoid;

  // Set correct answer
  form.querySelector(`input[name="correct-answer"][value="${currentQuestion.correct_ans}"]`).checked = true;

  // Close the details modal and open the "New Question" modal
  bootstrap.Modal.getInstance(document.getElementById('questionModal')).hide();
  const newQModal = new bootstrap.Modal(document.getElementById('newQuestionModal'));
  newQModal.show();
});

async function sendNewQuestionData() {
  const form = document.getElementById('newQuestionForm');

  const question_id = form.querySelector('#question_id').value || null;
  const title = form.querySelector('input[name="nq-title"]').value;
  const ans_a = form.querySelector('input[name="nq-a"]').value;
  const ans_b = form.querySelector('input[name="nq-b"]').value;
  const ans_c = form.querySelector('input[name="nq-c"]').value;
  const ans_d = form.querySelector('input[name="nq-d"]').value;
  const factoid = form.querySelector('textarea[name="factoid"]').value;

  const correctRadio = form.querySelector('input[name="correct-answer"]:checked');
  if (!correctRadio) {
    alert('Please select the correct answer');
    return;
  }
  const correct_ans = parseInt(correctRadio.value);

  const data = { title, ans_a, ans_b, ans_c, ans_d, factoid, correct_ans };

  try {
    const url = question_id ? `/api/questions/${question_id}` : '/api/questions';
    const method = question_id ? 'PUT' : 'POST';

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const result = await response.json();
    console.log('Question saved:', result);

    // Reset form and close modal
    form.reset();
    form.querySelector('#question_id').value = '';
    const modalEl = document.getElementById('newQuestionModal');
    bootstrap.Modal.getInstance(modalEl).hide();

    refreshQuestionList();
    alert('Question saved successfully!');
  } catch (err) {
    console.error(err);
    alert('Failed to save question.');
  }
}
